"""
detection_service.py
--------------------------------------------------
Detection Service
Uses detector.py to perform person detection.
--------------------------------------------------
Author : Ved Rathod
"""

from detector import CrowdDetector


class DetectionService:

    def __init__(self):

        self.detector = None

    # --------------------------------------------------
    # Load YOLO Detector
    # --------------------------------------------------

    def start(self):

        if self.detector is None:

            self.detector = CrowdDetector()

            print("✅ Detection Service Started")

    # --------------------------------------------------
    # Detect People
    # --------------------------------------------------

    def detect_people(self, frame):

        if self.detector is None:
            raise Exception("Detection Service Not Started")

        people = self.detector.detect(frame)

        return people

    # --------------------------------------------------
    # Count People
    # --------------------------------------------------

    def count_people(self, people):

        if self.detector is None:
            raise Exception("Detection Service Not Started")

        return self.detector.count(people)

    # --------------------------------------------------
    # Draw Bounding Boxes
    # --------------------------------------------------

    def draw_people(self, frame, people):

        if self.detector is None:
            raise Exception("Detection Service Not Started")

        return self.detector.draw(frame, people)

    # --------------------------------------------------
    # Get Complete Detection Result
    # --------------------------------------------------

    def process_frame(self, frame):

        people = self.detect_people(frame)

        count = self.count_people(people)

        output_frame = self.draw_people(frame.copy(), people)

        return {

            "people": people,

            "count": count,

            "frame": output_frame

        }

    # --------------------------------------------------
    # Stop Detection Service
    # --------------------------------------------------

    def stop(self):

        print("✅ Detection Service Stopped")