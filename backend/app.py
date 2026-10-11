"""
app.py
---------------------------------------------------------
AI Crowd Surveillance System — Enterprise Backend Server
Main Application Entry Point (Headless Production Mode)
---------------------------------------------------------
Author : Ved Rathod (Refactored)
"""

import os
import sys

# Ensure backend directory is in sys.path when running from outside directories
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import cv2
import time
import argparse
import traceback
import threading
import logging

from flask import Flask
from flask_cors import CORS
from api.routes import api
from core.shared_services import container
from models.state import state
from core.logging_config import setup_logging, get_logger

# -------------------------------
# Enterprise Logging Setup
# -------------------------------
setup_logging("logs/surveillance.log")
logger = get_logger("AI_Surveillance.Main")

# -------------------------------
# Flask Application Setup
# -------------------------------
app = Flask(__name__)
CORS(app)
app.register_blueprint(api)


@app.route("/")
def home():
    return {
        "message": "AI Crowd Surveillance Enterprise API Running",
        "status": "OK",
        "version": "2.0-Enterprise"
    }


def start_flask(port: int = 5000, production: bool = False):
    """
    Runs API server in a background thread.
    Uses multi-threaded Flask server by default to ensure real-time MJPEG video
    streaming without WSGI chunk buffering.
    """
    if production:
        try:
            from waitress import serve
            logger.info(f"✅ Starting Waitress Production WSGI server on 0.0.0.0:{port} (8 threads)")
            serve(app, host="0.0.0.0", port=port, threads=8)
            return
        except ImportError:
            logger.warning("⚠️ Waitress WSGI not installed. Falling back to multi-threaded Flask server.")
    
    logger.info(f"✅ Starting Real-Time Multi-Threaded Streaming API on 0.0.0.0:{port}")
    app.run(
        host="0.0.0.0",
        port=port,
        debug=False,
        use_reloader=False,
        threaded=True
    )


def run_surveillance_pipeline(gui_mode=False):
    """
    Main real-time surveillance processing loop.
    Runs YOLO tracking, ESP8266 sensor fusion, AI risk analytics, heatmap generation,
    and alert evaluation.
    In default production mode (gui_mode=False), cv2.imshow() is disabled and frames
    are streamed via MJPEG over /api/camera and /api/heatmap.
    """
    logger.info("=" * 60)
    logger.info("AI Crowd Surveillance System — Enterprise Pipeline")
    logger.info("=" * 60)

    try:
        container.start_all()
        logger.info("\n✅ Real-Time Surveillance Pipeline Started\n")

        while True:
            start_time = time.time()

            # 1. Read Camera Frame
            frame = container.camera.get_frame()
            if frame is None:
                time.sleep(0.05)
                continue

            # 2. Process YOLOv8 Crowd Tracking
            tracking_result = container.tracker.process_frame(frame)
            if tracking_result is None:
                continue

            # 3. Update Real-Time Crowd Density Heatmap
            container.heatmap.update(
                tracking_result.get("people", []),
                frame=frame
            )

            # 4. Read Hardware Sensor Data (ESP8266)
            sensor_data = container.sensor.read()
            if sensor_data is None:
                continue

            # 5. Process AI Analytics & Update Centralized State
            analytics_result = container.analytics.process(
                tracking_result,
                sensor_data
            )
            if analytics_result is None:
                continue

            # 6. Evaluate Emergency Alerts
            container.alerts.process(analytics_result)

            # 7. Optional Local Debug Window (Disabled in standard Production mode)
            if gui_mode:
                output_frame = tracking_result.get("frame", frame)
                cv2.imshow("AI Crowd Surveillance (Debug Mode)", output_frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    logger.info("\n🛑 Shutting down surveillance system...")
                    break

            # Rate limit main pipeline loop ~30 FPS max
            elapsed = time.time() - start_time
            if elapsed < 0.033:
                time.sleep(0.033 - elapsed)

    except KeyboardInterrupt:
        logger.info("\n🛑 Received exit signal. Stopping server...")
    except Exception as e:
        logger.error(f"\n❌ Pipeline ERROR: {e}")
        traceback.print_exc()
    finally:
        container.stop_all()
        if gui_mode:
            cv2.destroyAllWindows()
        logger.info("\n✅ AI Crowd Surveillance System successfully shut down.")


def main():
    parser = argparse.ArgumentParser(description="AI Crowd Surveillance System Backend")
    parser.add_argument(
        "--gui",
        action="store_true",
        help="Enable local OpenCV debug window (cv2.imshow). Default is headless production server."
    )
    parser.add_argument(
        "--port",
        type=int,
        default=5000,
        help="Port to listen on (default: 5000)"
    )
    parser.add_argument(
        "--dev",
        action="store_true",
        help="Run using Flask development server instead of Waitress WSGI production server."
    )
    args = parser.parse_args()

    # Start API daemon thread
    flask_thread = threading.Thread(
        target=start_flask,
        kwargs={"port": args.port, "production": False},
        daemon=True
    )
    flask_thread.start()
    logger.info(f"✅ Enterprise API Server thread launched on port {args.port}")

    # Start main surveillance pipeline
    run_surveillance_pipeline(gui_mode=args.gui)


if __name__ == "__main__":
    main()