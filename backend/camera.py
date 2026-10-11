"""
camera.py
---------------------------------------
Enterprise Hardware Camera Wrapper
Handles camera operations for:
1. Laptop Webcam / USB Camera
2. Auto-reconnection logic
3. Fallback synthetic frame generation when camera is offline
---------------------------------------
Author : Ved Rathod (Refactored)
"""

import cv2
import time
import logging
import numpy as np
from datetime import datetime
from config import (
    CAMERA_INDEX,
    FRAME_WIDTH,
    FRAME_HEIGHT,
    FPS
)

logger = logging.getLogger("AI_Surveillance.Camera")
logging.basicConfig(level=logging.INFO)


class Camera:
    """
    Hardware Camera access layer with automatic reconnection and fallback handling.
    """

    def __init__(self):
        self.camera_index = CAMERA_INDEX
        self.width = FRAME_WIDTH
        self.height = FRAME_HEIGHT
        self.fps = FPS
        self.cap = None
        self.connected = False
        self.last_reconnect_try = 0
        self.reconnect_interval = 5.0  # seconds between reconnect attempts

        self._connect()

    def _connect(self):
        """
        Attempts to connect or reconnect to the hardware camera.
        """
        try:
            if self.cap is not None:
                self.cap.release()

            self.cap = cv2.VideoCapture(self.camera_index)

            if self.cap.isOpened():
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
                self.cap.set(cv2.CAP_PROP_FPS, self.fps)
                self.connected = True
                logger.info(f"✅ Hardware Camera connected on index {self.camera_index}")
            else:
                self.connected = False
                logger.warning(f"⚠️ Unable to open hardware camera on index {self.camera_index}. Fallback frame active.")
        except Exception as e:
            self.connected = False
            logger.error(f"❌ Exception connecting to hardware camera: {e}")

    def _generate_fallback_frame(self):
        """
        Generates a synthetic diagnostic frame when hardware camera is disconnected.
        """
        frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        # Slate blue dark background
        frame[:] = (40, 30, 20)

        title = "AI SURVEILLANCE - CAMERA OFFLINE"
        subtitle = "Attempting Automatic Hardware Reconnection..."
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cv2.putText(frame, title, (50, int(self.height / 2) - 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 165, 255), 3)
        cv2.putText(frame, subtitle, (50, int(self.height / 2) + 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (200, 200, 200), 2)
        cv2.putText(frame, f"Timestamp: {timestamp}", (50, int(self.height / 2) + 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        return frame

    def read(self):
        """
        Reads a frame from the camera. Automatically attempts reconnect if disconnected.
        Returns a valid frame (hardware frame or fallback diagnostic frame).
        """
        if not self.connected or self.cap is None or not self.cap.isOpened():
            current_time = time.time()
            if current_time - self.last_reconnect_try > self.reconnect_interval:
                self.last_reconnect_try = current_time
                logger.info("🔄 Attempting camera hardware reconnect...")
                self._connect()
            return self._generate_fallback_frame()

        try:
            success, frame = self.cap.read()
            if not success or frame is None:
                logger.warning("⚠️ Failed to read frame from camera. Marking as disconnected.")
                self.connected = False
                return self._generate_fallback_frame()
            return frame
        except Exception as e:
            logger.error(f"❌ Exception reading camera frame: {e}")
            self.connected = False
            return self._generate_fallback_frame()

    def info(self):
        """
        Returns diagnostic information about the camera stream.
        """
        if self.connected and self.cap is not None:
            width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
            height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
            fps = self.cap.get(cv2.CAP_PROP_FPS)
        else:
            width = float(self.width)
            height = float(self.height)
            fps = float(self.fps)

        return {
            "width": width,
            "height": height,
            "fps": fps,
            "connected": self.connected
        }

    def is_connected(self):
        return self.connected

    def release(self):
        """
        Releases the hardware camera handle.
        """
        if self.cap is not None:
            try:
                self.cap.release()
            except Exception:
                pass
        self.connected = False
        logger.info("✅ Camera hardware released.")


if __name__ == "__main__":
    camera = Camera()
    print("Camera info:", camera.info())
    frame = camera.read()
    print("Read frame shape:", frame.shape if frame is not None else None)
    camera.release()