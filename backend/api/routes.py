"""
routes.py
----------------------------------------------------
Enterprise Flask API Routes
Supports:
- Clean status & dashboard endpoints
- Adaptively formatted historical endpoints:
  - Default GET /api/history returns clean list
  - Paginated GET /api/history?page=1&per_page=50&range=24h returns paginated dict
- Live MJPEG streaming (/api/camera, /api/heatmap)
----------------------------------------------------
Author : Ved Rathod (Refactored)
"""

from flask import Blueprint, jsonify, Response, request
import os
import cv2
import base64
import tempfile
import numpy as np
from core.shared_services import container
from models.state import state
from core.health_monitor import health_monitor
from repositories.sensor_repository import SensorRepository
from repositories.health_repository import HealthRepository
from database import db

api = Blueprint("api", __name__)


# ----------------------------------------------------
# Real-Time System Status & Metrics
# URL: /api/status
# ----------------------------------------------------
@api.route("/api/status", methods=["GET"])
def system_status():
    return jsonify(state.to_dict())


# ----------------------------------------------------
# Consolidated Dashboard Payload
# URL: /api/dashboard
# ----------------------------------------------------
@api.route("/api/dashboard", methods=["GET"])
def dashboard_payload():
    return jsonify(state.get_dashboard_payload())


# ----------------------------------------------------
# Real-Time System Health Monitoring & Probes
# URLs:
# - /api/health         : Basic system health
# - /api/health/live    : Kubernetes liveness probe (200 OK)
# - /api/health/ready   : Kubernetes readiness probe (200 OK or 503 Service Unavailable)
# - /api/health/metrics : Detailed subsystem metrics
# ----------------------------------------------------
@api.route("/api/health", methods=["GET"])
def system_health():
    return jsonify(state.get_system_health())


@api.route("/api/health/live", methods=["GET"])
def health_liveness():
    """
    Kubernetes/Docker liveness probe endpoint.
    """
    return jsonify(health_monitor.get_liveness()), 200


@api.route("/api/health/ready", methods=["GET"])
def health_readiness():
    """
    Kubernetes/Docker readiness probe endpoint.
    Returns 200 OK if DB and AI Model are healthy, else 503 Service Unavailable.
    """
    data = health_monitor.get_readiness()
    status_code = 200 if data["ready"] else 503
    return jsonify(data), status_code


@api.route("/api/health/metrics", methods=["GET"])
def health_metrics():
    """
    Detailed production telemetry endpoint with deep subsystem latency and resource checks.
    """
    return jsonify(health_monitor.get_detailed_metrics()), 200


# ----------------------------------------------------
# Real-Time Active Alerts Buffer
# URL: /api/alerts
# ----------------------------------------------------
@api.route("/api/alerts", methods=["GET"])
def alerts():
    return jsonify(state.get_alerts())


# ----------------------------------------------------
# Historical Paginated Endpoints with Range Filtering
# Supports query params:
# ?page=1&per_page=50&range=1h|24h|7d|all
# ----------------------------------------------------

@api.route("/api/history", methods=["GET"])
def history():
    """
    Crowd surveillance logs from crowd_log table.
    Returns list by default; returns paginated dict if page/per_page/range specified.
    """
    is_paginated = any(param in request.args for param in ("page", "per_page", "range"))
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 50, type=int)
    time_range = request.args.get("range", "all", type=str)

    try:
        if hasattr(container.analytics, "crowd_repo") and container.analytics.crowd_repo:
            data = container.analytics.crowd_repo.get_paginated(
                page=page,
                per_page=per_page,
                time_range=time_range
            )
            return jsonify(data if is_paginated else data["items"])
    except Exception as e:
        if is_paginated:
            return jsonify({"error": str(e), "items": [], "total": 0, "page": page, "pages": 1}), 500
        return jsonify([])

    return jsonify({"items": [], "total": 0, "page": page, "per_page": per_page, "pages": 1} if is_paginated else [])


# ----------------------------------------------------
# AI Model Evaluation Endpoints
# Separated from Live Monitoring Data
# ----------------------------------------------------

@api.route("/api/evaluation", methods=["GET"])
def get_evaluation():
    """
    Returns the latest AI Model Evaluation result from the database.
    """
    try:
        latest = db.get_latest_evaluation_result()
        if latest:
            return jsonify(latest)
        return jsonify({"error": "No evaluation data found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api.route("/api/model_accuracy", methods=["GET"])
def get_model_accuracy():
    """
    Returns just the accuracy metric of the latest evaluation.
    """
    try:
        latest = db.get_latest_evaluation_result()
        if latest:
            return jsonify({"accuracy": latest.get("accuracy", 0.0)})
        return jsonify({"accuracy": 0.0})
    except Exception:
        return jsonify({"accuracy": 0.0}), 500


@api.route("/api/confusion_matrix", methods=["GET"])
def get_confusion_matrix():
    """
    Returns just the confusion matrix of the latest evaluation.
    """
    try:
        latest = db.get_latest_evaluation_result()
        if latest:
            return jsonify({
                "tp": latest.get("tp", 0),
                "fp": latest.get("fp", 0),
                "fn": latest.get("fn", 0),
                "tn": latest.get("tn", 0)
            })
        return jsonify({"tp": 0, "fp": 0, "fn": 0, "tn": 0})
    except Exception:
        return jsonify({"tp": 0, "fp": 0, "fn": 0, "tn": 0}), 500


@api.route("/api/alerts/history", methods=["GET"])
def alerts_history():
    """
    Alert logs from alerts table.
    """
    is_paginated = any(param in request.args for param in ("page", "per_page", "range", "level"))
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 50, type=int)
    time_range = request.args.get("range", "all", type=str)
    level_filter = request.args.get("level", None, type=str)

    try:
        data = container.alerts.repository.get_paginated(
            page=page,
            per_page=per_page,
            time_range=time_range,
            level_filter=level_filter
        )
        return jsonify(data if is_paginated else data["items"])
    except Exception as e:
        if is_paginated:
            return jsonify({"error": str(e), "items": [], "total": 0, "page": page, "pages": 1}), 500
        return jsonify([])


@api.route("/api/sensors/history", methods=["GET"])
def sensors_history():
    """
    Hardware sensor logs from sensor_log table.
    """
    is_paginated = any(param in request.args for param in ("page", "per_page", "range"))
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 50, type=int)
    time_range = request.args.get("range", "all", type=str)

    repo = SensorRepository()
    try:
        data = repo.get_paginated(page=page, per_page=per_page, time_range=time_range)
        return jsonify(data if is_paginated else data["items"])
    finally:
        repo.close()


@api.route("/api/health/history", methods=["GET"])
def health_history():
    """
    System health history from system_health table.
    """
    is_paginated = any(param in request.args for param in ("page", "per_page", "range"))
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 50, type=int)
    time_range = request.args.get("range", "all", type=str)

    repo = HealthRepository()
    try:
        data = repo.get_paginated(page=page, per_page=per_page, time_range=time_range)
        return jsonify(data if is_paginated else data["items"])
    finally:
        repo.close()


# =====================================================
# Live MJPEG Camera Stream
# URL: /api/camera
# =====================================================
@api.route("/api/camera", methods=["GET"])
def camera_stream():
    return Response(
        container.camera.generate_frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )

@api.route("/api/camera/toggle", methods=["POST"])
def toggle_camera():
    action = request.json.get("action")
    if action == "stop":
        container.camera.stop()
        return jsonify({"success": True, "message": "Camera stopped"})
    elif action == "start":
        container.camera.start()
        return jsonify({"success": True, "message": "Camera started"})
    return jsonify({"success": False, "error": "Invalid action"}), 400



# =====================================================
# Live MJPEG YOLO Crowd Density Heatmap Stream
# URL: /api/heatmap
# =====================================================
@api.route("/api/heatmap", methods=["GET"])
def heatmap_stream():
    return Response(
        container.heatmap.generate_heatmap_frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )


# =====================================================
# AI Media Crowd Analysis (Image & Video Upload)
# URL: /api/analyze_media
# =====================================================
@api.route("/api/analyze_media", methods=["POST"])
def analyze_media():
    """
    Accepts uploaded image or video file, runs YOLOv8 crowd tracking,
    and returns annotated frame Base64 data URL + crowd metrics & risk status.
    """
    if "file" not in request.files:
        return jsonify({"success": False, "error": "No file uploaded"}), 400

    file = request.files["file"]
    if not file or file.filename == "":
        return jsonify({"success": False, "error": "Empty filename"}), 400

    ext = os.path.splitext(file.filename)[1].lower()
    image_exts = [".jpg", ".jpeg", ".png", ".bmp", ".webp"]
    video_exts = [".mp4", ".avi", ".mov", ".mkv", ".webm"]

    count = 0
    avg_conf = 0.0
    annotated_frame = None

    try:
        if ext in image_exts:
            file_bytes = file.read()
            np_arr = np.frombuffer(file_bytes, np.uint8)
            img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            if img is None:
                return jsonify({"success": False, "error": "Failed to decode image"}), 400

            result = container.detector.process_frame(img)
            count = result.get("count", 0)
            people = result.get("people", [])
            avg_conf = sum(p.get("confidence", 0) for p in people) / len(people) if people else 0.0
            annotated_frame = result.get("frame", img)

        elif ext in video_exts:
            with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as temp_file:
                temp_path = temp_file.name
                file.save(temp_path)

            try:
                cap = cv2.VideoCapture(temp_path)
                max_count = 0
                best_frame = None
                frame_idx = 0

                while cap.isOpened():
                    ret, frame = cap.read()
                    if not ret or frame is None:
                        break
                    # Sample every 5th frame up to 300 frames for speed
                    if frame_idx % 5 == 0:
                        result = container.tracker.process_frame(frame)
                        current_count = result.get("count", 0)
                        current_people = result.get("people", [])
                        current_conf = sum(p.get("confidence", 0) for p in current_people) / len(current_people) if current_people else 0.0

                        if current_count >= max_count or best_frame is None:
                            max_count = current_count
                            avg_conf = current_conf
                            best_frame = result.get("frame", frame)
                    frame_idx += 1
                    if frame_idx > 300:
                        break
                cap.release()
                count = max_count
                annotated_frame = best_frame
            finally:
                if os.path.exists(temp_path):
                    try:
                        os.remove(temp_path)
                    except Exception:
                        pass
        else:
            return jsonify({"success": False, "error": f"Unsupported format: {ext}"}), 400

        if annotated_frame is None:
            return jsonify({"success": False, "error": "No frames could be analyzed"}), 400

        # Compute enterprise analytics on detected count
        analysis = container.analytics.analytics.analyze(count, 100)
        risk_score = analysis.get("risk_score", 0)
        status_text = analysis.get("status", "SAFE")

        # Encode annotated image as Base64 JPEG
        success_enc, buffer = cv2.imencode(".jpg", annotated_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
        if not success_enc:
            return jsonify({"success": False, "error": "Failed to encode result image"}), 500

        b64_str = "data:image/jpeg;base64," + base64.b64encode(buffer).decode("utf-8")

        return jsonify({
            "success": True,
            "filename": file.filename,
            "count": count,
            "accuracy": round(avg_conf * 100, 1),
            "risk_score": risk_score,
            "status": status_text,
            "image_base64": b64_str
        }), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500