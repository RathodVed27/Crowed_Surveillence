"""
heatmap_service.py
--------------------------------------------------
Enterprise YOLO Crowd Density Heatmap Service
Generates real-time spatial density heatmaps from YOLO
person bounding boxes and streams via MJPEG.
--------------------------------------------------
Author : Ved Rathod (Refactored)
"""

import cv2
import time
import numpy as np
import logging
from models.state import state
from config import FRAME_WIDTH, FRAME_HEIGHT

logger = logging.getLogger("AI_Surveillance.HeatmapService")


class HeatmapService:
    """
    Generates a dynamic spatial density heatmap from YOLO detections.
    Accumulates person centroids over time with decay to show hot crowd zones.
    Overlays heatmap on the live camera frame for a professional result.
    """

    def __init__(self):
        self.width = FRAME_WIDTH
        self.height = FRAME_HEIGHT
        self.density_matrix = np.zeros((self.height, self.width), dtype=np.float32)
        self.decay_factor = 0.92
        self.kernel_size = 61
        self.kernel = self._create_gaussian_kernel(self.kernel_size, sigma=15.0)
        self.is_running = False
        self._last_frame = None  # Store last camera frame for fallback

    def _create_gaussian_kernel(self, size, sigma):
        """
        Creates a 2D Gaussian kernel patch for adding smooth hot spots.
        """
        ax = np.linspace(-(size - 1) / 2.0, (size - 1) / 2.0, size)
        xx, yy = np.meshgrid(ax, ax)
        kernel = np.exp(-0.5 * (np.square(xx) + np.square(yy)) / np.square(sigma))
        return kernel.astype(np.float32) * 50.0

    def start(self):
        self.density_matrix = np.zeros((self.height, self.width), dtype=np.float32)
        self.is_running = True
        logger.info("✅ Heatmap Service Started")

    def update(self, people, frame=None, frame_shape=None):
        """
        Updates density matrix with current YOLO person bounding boxes.
        Generates colored heatmap image blended over the camera frame.
        """
        # Determine frame dimensions from the ACTUAL camera frame
        if frame is not None:
            h, w = frame.shape[:2]
            self._last_frame = frame.copy()
        elif frame_shape is not None:
            h, w = frame_shape[:2]
        else:
            h, w = self.height, self.width

        # Resize density matrix if camera resolution changed or mismatched
        if (h, w) != (self.density_matrix.shape[0], self.density_matrix.shape[1]):
            self.height, self.width = h, w
            self.density_matrix = np.zeros((h, w), dtype=np.float32)
            logger.info(f"Heatmap resized to match camera: {w}x{h}")

        # Apply temporal decay so old positions fade out
        self.density_matrix *= self.decay_factor

        # Add Gaussian spot for each detected person centroid
        half_k = self.kernel_size // 2
        for person in people:
            bbox = person.get("bbox")
            if not bbox:
                continue
            x1, y1, x2, y2 = bbox
            cx = int((x1 + x2) / 2)
            cy = int((y1 + 3 * y2) / 4)  # Lower body / foot contact area

            # Calculate bounds in density matrix
            y_min = max(0, cy - half_k)
            y_max = min(h, cy + half_k + 1)
            x_min = max(0, cx - half_k)
            x_max = min(w, cx + half_k + 1)

            # Calculate corresponding kernel slice bounds
            ky_min = half_k - (cy - y_min)
            ky_max = half_k + (y_max - cy)
            kx_min = half_k - (cx - x_min)
            kx_max = half_k + (x_max - cx)

            if y_max > y_min and x_max > x_min:
                self.density_matrix[y_min:y_max, x_min:x_max] += self.kernel[ky_min:ky_max, kx_min:kx_max]

        # Smooth the density for beautiful gradient transitions (like world heatmap)
        smoothed = cv2.GaussianBlur(self.density_matrix, (31, 31), 0)

        # Clamp to [0, 255]
        clipped = np.clip(smoothed, 0, 255).astype(np.uint8)

        # Apply JET colormap — gives the blue → cyan → green → yellow → red look
        heatmap_colored = cv2.applyColorMap(clipped, cv2.COLORMAP_JET)

        state.set_heatmap_frame(heatmap_colored)
        return heatmap_colored

    def _generate_fallback_heatmap(self):
        """
        Generates placeholder heatmap frame when system is warming up.
        Uses the last known camera frame if available, otherwise a dark placeholder.
        """
        if self._last_frame is not None:
            frame = self._last_frame.copy()
            # Dim the frame slightly to show it's a fallback
            frame = (frame.astype(np.float32) * 0.5).astype(np.uint8)
        else:
            frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
            frame[:] = (30, 10, 50)

        cv2.putText(
            frame,
            "HEATMAP WAITING FOR CAMERA...",
            (50, int(frame.shape[0] / 2)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            (255, 200, 200),
            2
        )
        return frame

    def generate_heatmap_frames(self):
        """
        High-performance MJPEG generator for Flask /api/heatmap stream.
        """
        while True:
            frame = state.get_heatmap_frame()
            if frame is None:
                frame = self._generate_fallback_heatmap()

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
                logger.error(f"Error encoding MJPEG heatmap frame: {e}")
                time.sleep(0.05)
            time.sleep(0.033)  # ~30 FPS

    def reset(self):
        self.density_matrix = np.zeros((self.height, self.width), dtype=np.float32)

    def stop(self):
        self.is_running = False
        self._last_frame = None
        logger.info("✅ Heatmap Service Stopped")

