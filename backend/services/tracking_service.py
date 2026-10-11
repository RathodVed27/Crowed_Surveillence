"""
tracking_service.py
--------------------------------------------------
Enterprise Tracking Service
Uses Ultralytics YOLOv8 + ByteTrack to detect and track people.
Calculates occupancy, unique visitor count, and real-time FPS.
--------------------------------------------------
Author : Ved Rathod (Refactored)
"""

import time
import logging
from tracker import CrowdTracker
from models.state import state

logger = logging.getLogger("AI_Surveillance.TrackingService")


class TrackingService:
    """
    Manages crowd tracking, occupancy counting, and FPS measurement.
    """

    def __init__(self):
        self.tracker = None
        self.entry_count = 0
        self.exit_count = 0
        self.current_people = 0
        self.unique_ids = set()
        self._last_time = time.time()
        self._fps_smooth = 0.0

    def start(self):
        """
        Starts the YOLO ByteTrack tracker model.
        """
        if self.tracker is None:
            try:
                self.tracker = CrowdTracker()
                state.update_health_status(ai_status="READY")
                logger.info("✅ Tracking Service Started")
            except Exception as e:
                state.update_health_status(ai_status="ERROR")
                logger.error(f"❌ Error starting YOLO tracker: {e}")
                raise

    def process_frame(self, frame):
        """
        Runs tracking on camera frame, calculates FPS, and returns tracking metadata.
        """
        if self.tracker is None:
            raise Exception("Tracking Service Not Started")

        start_time = time.time()

        results = self.tracker.track(frame)
        people = self.tracker.get_people(results)
        count = self.tracker.count(people)
        output = self.tracker.draw(frame.copy(), people)

        # Calculate instant & smoothed FPS
        elapsed = time.time() - start_time
        instant_fps = 1.0 / max(elapsed, 0.001)
        if self._fps_smooth == 0.0:
            self._fps_smooth = instant_fps
        else:
            self._fps_smooth = self._fps_smooth * 0.8 + instant_fps * 0.2

        # Peak-hold smoothing to prevent UI flickering on momentary dropouts
        if not hasattr(self, "_hold_count"):
            self._hold_count = 0
            self._hold_timer = 0

        if count >= self._hold_count:
            self._hold_count = count
            self._hold_timer = 45  # Hold peak count for ~45 frames (1.5s)
        else:
            self._hold_timer -= 1
            if self._hold_timer <= 0:
                self._hold_count = count

        self.current_people = self._hold_count

        # Only add confident detections to unique visitor IDs
        for person in people:
            if person.get("id") is not None and person.get("confidence", 0) >= 0.45:
                self.unique_ids.add(person["id"])

        # Update SystemHealth FPS
        state.update_health_status(fps=self._fps_smooth)

        return {
            "frame": output,
            "people": people,
            "count": self.current_people,
            "occupancy": self.current_people,
            "entry": self.entry_count,
            "exit": self.exit_count,
            "unique": len(self.unique_ids),
            "fps": round(self._fps_smooth, 1)
        }

    def get_statistics(self):
        return {
            "occupancy": self.current_people,
            "entry": self.entry_count,
            "exit": self.exit_count,
            "unique": len(self.unique_ids),
            "fps": round(self._fps_smooth, 1)
        }

    def reset(self):
        self.entry_count = 0
        self.exit_count = 0
        self.current_people = 0
        self.unique_ids.clear()
        self._fps_smooth = 0.0

    def stop(self):
        logger.info("✅ Tracking Service Stopped")