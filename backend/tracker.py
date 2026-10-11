"""
tracker.py
----------------------------------------------------
Professional Crowd Tracker
Uses Ultralytics + ByteTrack
----------------------------------------------------
"""

from ultralytics import YOLO
from config import YOLO_MODEL, HEAD_CLASS, PERSON_CLASS, USE_HEAD_DETECTION


class CrowdTracker:

    def __init__(self):

        model_type = "Head Detection" if USE_HEAD_DETECTION else "General Person"
        print(f"Loading YOLO Tracker ({model_type})...")

        self.model = YOLO(str(YOLO_MODEL))

        # Use the correct class ID based on which model is loaded
        self.target_class = HEAD_CLASS if USE_HEAD_DETECTION else PERSON_CLASS

        print("Tracker Ready")

    # -------------------------------------------------

    def track(self, frame):

        results = self.model.track(

            frame,

            persist=True,

            tracker="trackers/bytetrack.yaml",

            verbose=False

        )

        return results

    # -------------------------------------------------

    def get_people(self, results):

        people = []

        if not results:
            return people

        result = results[0]

        if result.boxes is None:
            return people

        for box in result.boxes:

            if int(box.cls[0]) != self.target_class:
                continue

            x1, y1, x2, y2 = map(int, box.xyxy[0])

            confidence = float(box.conf[0])

            track_id = None

            if box.id is not None:
                track_id = int(box.id[0])

            people.append({

                "id": track_id,

                "bbox": (x1, y1, x2, y2),

                "confidence": confidence

            })

        return people

    # -------------------------------------------------

    def count(self, people):

        return len(people)

    # -------------------------------------------------

    def draw(self, frame, people):

        import cv2

        for person in people:

            x1, y1, x2, y2 = person["bbox"]

            person_id = person["id"]

            confidence = person["confidence"]

            cv2.rectangle(

                frame,

                (x1, y1),

                (x2, y2),

                (0,255,0),

                2

            )

            label = f"ID:{person_id} {confidence:.2f}"

            cv2.putText(

                frame,

                label,

                (x1,y1-10),

                cv2.FONT_HERSHEY_SIMPLEX,

                0.5,

                (0,255,0),

                2

            )

        return frame