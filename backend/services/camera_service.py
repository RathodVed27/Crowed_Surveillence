"""
camera_service.py
--------------------------------------------------
Enterprise Camera Service
Manages hardware camera access, frame acquisition, and
high-performance MJPEG streaming of processed YOLO frames.
--------------------------------------------------
Author : Ved Rathod (Refactored)
"""

import cv2
import time
import numpy as np
import logging
from camera import Camera
from models.state import state
from config import FRAME_WIDTH, FRAME_HEIGHT

logger = logging.getLogger("AI_Surveillance.CameraService")


class CameraService:
    """
    Service layer wrapping hardware Camera.
    Provides MJPEG frame generator streaming annotated YOLO frames from SystemState,
    with automatic fallback images when camera is offline or initializing.
    """

    def __init__(self):
        self.camera = None
        self.is_running = False

    def start(self):
        """
        Starts the camera service and underlying hardware camera.
        """
        if self.camera is None:
            self.camera = Camera()
            self.is_running = True
            state.update_health_status(camera_connected=self.camera.is_connected())
            logger.info("✅ Camera Service Started")

    def get_frame(self):
        """
        Reads raw frame from camera.
        """
        if self.camera is None:
            return None
        frame = self.camera.read()
        state.update_health_status(camera_connected=self.camera.is_connected())
        return frame

    def _generate_fallback_stream_frame(self):
        """
        Generates synthetic placeholder frame when camera is initializing or offline.
        """
        frame = np.zeros((FRAME_HEIGHT, FRAME_WIDTH, 3), dtype=np.uint8)
        frame[:] = (25, 25, 35)
        cv2.putText(
            frame,
            "AI SURVEILLANCE - WAITING FOR CAMERA STREAM...",
            (60, int(FRAME_HEIGHT / 2)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            (255, 200, 100),
            2
        )
        return frame

    def generate_frames(self):
        """
        High-performance MJPEG generator for Flask /api/camera stream.
        Streams the latest YOLO-annotated frame from SystemState, avoiding duplicate YOLO inference.
        If no frame is ready, streams a diagnostic standby image.
        """
        while True:
            # Prefer annotated frame from state; fall back to raw frame if state frame is None
            frame = state.get_frame()
            if frame is None:
                frame = self.get_frame()

            if frame is None:
                frame = self._generate_fallback_stream_frame()

            try:
                success, buffer = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
                if not success:
                    time.sleep(0.02)
                    continue

                frame_bytes = buffer.tobytes()

                yield (
                    b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n'
                    + frame_bytes +
                    b'\r\n'
                )
            except Exception as e:
                logger.error(f"Error encoding MJPEG frame: {e}")
                time.sleep(0.05)
            time.sleep(0.033)  # Rate limit stream ~30 FPS

    def get_info(self):
        """
        Returns camera diagnostic info.
        """
        if self.camera is None:
            return {"connected": False}
        return self.camera.info()

    def stop(self):
        """
        Stops camera service and releases resources.
        """
        if self.camera is not None:
            self.camera.release()
            self.camera = None
            self.is_running = False
            state.update_health_status(camera_connected=False)
            state.set_frame(None)
            state.set_heatmap_frame(None)
            cv2.destroyAllWindows()
            logger.info("✅ Camera Service Stopped")