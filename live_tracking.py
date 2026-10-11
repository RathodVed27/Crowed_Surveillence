import cv2
import time
from ultralytics import YOLO


# ============================================================
# CONFIGURATION
# ============================================================

# Standard YOLOv8 model for live PERSON detection
MODEL_PATH = r"F:\Crowed_Surveillence\yolov8n.pt"

CONFIDENCE = 0.35

CAMERA_INDEX = 0


# ============================================================
# LOAD MODEL
# ============================================================

print("Loading YOLOv8 person model...")

model = YOLO(MODEL_PATH)

print("YOLOv8 person model loaded successfully.")


# ============================================================
# OPEN CAMERA
# ============================================================

print("Opening camera...")

cap = cv2.VideoCapture(CAMERA_INDEX)

if not cap.isOpened():
    print("ERROR: Could not open camera.")
    exit()


cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)


print("Camera opened successfully.")
print("ByteTrack tracking started.")
print("Press Q to quit.")


# ============================================================
# FPS
# ============================================================

previous_time = time.time()


# ============================================================
# MAIN LOOP
# ============================================================

while True:

    success, frame = cap.read()

    if not success:
        print("ERROR: Could not read frame.")
        break


    # ========================================================
    # YOLO + BYTE TRACK
    # ========================================================

    results = model.track(
        source=frame,
        conf=CONFIDENCE,
        classes=[0],                 # COCO class 0 = person
        tracker="bytetrack.yaml",
        persist=True,
        device=0,
        verbose=False
    )

    result = results[0]


    # ========================================================
    # COUNT PEOPLE
    # ========================================================

    people_count = 0


    if result.boxes is not None:

        boxes = result.boxes.xyxy.cpu().numpy()
        scores = result.boxes.conf.cpu().numpy()
        classes = result.boxes.cls.cpu().numpy()


        # Get tracking IDs
        if result.boxes.id is not None:

            track_ids = (
                result.boxes.id
                .cpu()
                .numpy()
                .astype(int)
            )

        else:

            track_ids = [-1] * len(boxes)


        for box, score, cls, track_id in zip(
            boxes,
            scores,
            classes,
            track_ids
        ):

            # Only person class
            if int(cls) != 0:
                continue


            people_count += 1


            x1, y1, x2, y2 = map(
                int,
                box
            )


            # =================================================
            # DRAW PERSON BOX
            # =================================================

            cv2.rectangle(
                frame,
                (x1, y1),
                (x2, y2),
                (0, 255, 0),
                2
            )


            # =================================================
            # LABEL
            # =================================================

            if track_id >= 0:

                label = (
                    f"ID {track_id} | "
                    f"Person {score:.2f}"
                )

            else:

                label = (
                    f"ID ? | "
                    f"Person {score:.2f}"
                )


            cv2.putText(
                frame,
                label,
                (x1, max(25, y1 - 8)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (0, 255, 0),
                2
            )


    # ========================================================
    # FPS
    # ========================================================

    current_time = time.time()

    fps = 1 / max(
        current_time - previous_time,
        0.001
    )

    previous_time = current_time


    # ========================================================
    # INFORMATION PANEL
    # ========================================================

    cv2.rectangle(
        frame,
        (0, 0),
        (410, 130),
        (0, 0, 0),
        -1
    )


    cv2.putText(
        frame,
        "CROWD SURVEILLANCE",
        (15, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2
    )


    cv2.putText(
        frame,
        f"People: {people_count}",
        (15, 62),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.75,
        (0, 255, 0),
        2
    )


    cv2.putText(
        frame,
        f"FPS: {fps:.1f}",
        (15, 92),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 255),
        2
    )


    cv2.putText(
        frame,
        "Tracking: ByteTrack",
        (15, 118),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (255, 255, 255),
        1
    )


    # ========================================================
    # SHOW
    # ========================================================

    cv2.imshow(
        "Crowd Surveillance - YOLOv8 + ByteTrack",
        frame
    )


    # ========================================================
    # QUIT
    # ========================================================

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


# ============================================================
# CLEANUP
# ============================================================

cap.release()
cv2.destroyAllWindows()

print("Tracking stopped.")