"""
detector.py
-----------------------------------------
YOLO Person Detection Engine
-----------------------------------------
Author : Ved Rathod
"""

from ultralytics import YOLO
from config import YOLO_MODEL, CONFIDENCE, PERSON_CLASS, HEAD_CLASS, USE_HEAD_DETECTION


class CrowdDetector:

    def __init__(self):

        model_type = "Head Detection" if USE_HEAD_DETECTION else "General Person"
        print(f"Loading YOLO Model ({model_type})...")

        self.model = YOLO(str(YOLO_MODEL))

        # Use the correct class ID based on which model is loaded
        self.target_class = HEAD_CLASS if USE_HEAD_DETECTION else PERSON_CLASS

        print("YOLO Loaded Successfully")

    # --------------------------------------------------------
    # Detect People
    # --------------------------------------------------------

    def detect(self, frame):

        results = self.model(
            frame,
            conf=CONFIDENCE,
            verbose=False
        )

        people = []

        for result in results:

            for box in result.boxes:

                cls = int(box.cls[0])

                if cls != self.target_class:
                    continue

                x1, y1, x2, y2 = map(int, box.xyxy[0])

                confidence = float(box.conf[0])

                people.append({

                    "bbox": (x1, y1, x2, y2),

                    "confidence": confidence

                })

        return people

    # --------------------------------------------------------
    # Draw Bounding Boxes
    # --------------------------------------------------------

    def draw(self, frame, people):

        import cv2

        for person in people:

            x1, y1, x2, y2 = person["bbox"]

            confidence = person["confidence"]

            cv2.rectangle(
                frame,
                (x1, y1),
                (x2, y2),
                (0,255,0),
                2
            )

            cv2.putText(
                frame,
                f"{confidence:.2f}",
                (x1,y1-10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0,255,0),
                2
            )

        return frame

    # --------------------------------------------------------

    def count(self, people):

        return len(people)