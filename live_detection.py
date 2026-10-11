import cv2
import time
from ultralytics import YOLO


# ============================================================
# CONFIGURATION
# ============================================================

MODEL_PATH = r"F:\Crowed_Surveillence\runs\crowd_yolov8m_combined_tiled\weights\best.pt"

CONFIDENCE = 0.10

CAMERA_INDEX = 0


# ============================================================
# LOAD MODEL
# ============================================================

print("Loading YOLO model...")

model = YOLO(MODEL_PATH)

print("YOLO model loaded successfully.")


# ============================================================
# OPEN CAMERA
# ============================================================

print("Opening camera...")

cap = cv2.VideoCapture(CAMERA_INDEX)

if not cap.isOpened():
    print("ERROR: Could not open camera.")
    print("Try changing CAMERA_INDEX from 0 to 1.")
    exit()


# Camera resolution
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)


print("Camera opened successfully.")
print("Press Q to quit.")


# ============================================================
# FPS VARIABLES
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


    # --------------------------------------------------------
    # YOLO DETECTION
    # --------------------------------------------------------

    results = model.predict(
        source=frame,
        conf=CONFIDENCE,
        device=0,
        verbose=False
    )


    result = results[0]


    # --------------------------------------------------------
    # COUNT DETECTIONS
    # --------------------------------------------------------

    people_count = 0


    if result.boxes is not None:

        boxes = result.boxes.xyxy.cpu().numpy()
        scores = result.boxes.conf.cpu().numpy()
        classes = result.boxes.cls.cpu().numpy()


        for box, score, cls in zip(
            boxes,
            scores,
            classes
        ):

            # Class 0 = head/person class
            if int(cls) != 0:
                continue


            people_count += 1


            x1, y1, x2, y2 = map(
                int,
                box
            )


            # ------------------------------------------------
            # DRAW BOX
            # ------------------------------------------------

            cv2.rectangle(
                frame,
                (x1, y1),
                (x2, y2),
                (0, 255, 0),
                2
            )


            # ------------------------------------------------
            # CONFIDENCE
            # ------------------------------------------------

            label = f"Head {score:.2f}"


            cv2.putText(
                frame,
                label,
                (x1, max(20, y1 - 5)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                1
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
        (350, 100),
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
        (15, 60),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 0),
        2
    )


    cv2.putText(
        frame,
        f"FPS: {fps:.1f}",
        (15, 90),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 255),
        2
    )


    # ========================================================
    # DISPLAY
    # ========================================================

    cv2.imshow(
        "Crowd Surveillance - YOLOv8",
        frame
    )


    # Press Q to quit
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


# ============================================================
# CLEANUP
# ============================================================

cap.release()

cv2.destroyAllWindows()

print("Camera stopped.")