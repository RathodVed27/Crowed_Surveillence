from ultralytics import YOLO
import cv2
import serial
from pathlib import Path

# -------------------------
# Serial Port
# -------------------------
ser = serial.Serial("COM3",115200,timeout=1)

# -------------------------
# Load YOLO (auto-detect trained model)
# -------------------------
TRAINED_MODEL = Path(__file__).parent.parent / "backend" / "models" / "crowd_head_model.pt"
DEFAULT_MODEL = "yolov8n.pt"

if TRAINED_MODEL.exists():
    model = YOLO(str(TRAINED_MODEL))
    TARGET_CLASS = 0  # head class in trained model
    print(f"Using trained head detection model")
else:
    model = YOLO(DEFAULT_MODEL)
    TARGET_CLASS = 0  # person class in COCO
    print(f"Using default YOLO model (train a model for better accuracy)")

# -------------------------
# Camera
# -------------------------
cap = cv2.VideoCapture(0)

piezo = 0
ir = 0
sw = 0

while True:

    # -------------------------
    # Read Serial
    # -------------------------
    if ser.in_waiting:

        line = ser.readline().decode().strip()

        try:
            piezo,ir,sw = map(int,line.split(","))
        except:
            pass

    # -------------------------
    # Camera
    # -------------------------
    ret,frame = cap.read()

    if not ret:
        break

    # -------------------------
    # YOLO
    # -------------------------
    results = model(frame,verbose=False)

    people = 0

    for result in results:

        for box in result.boxes:

            cls = int(box.cls[0])

            if cls == TARGET_CLASS:
                people += 1

    frame = results[0].plot()

    # -------------------------
    # Display Information
    # -------------------------

    cv2.putText(frame,
                f"People : {people}",
                (20,35),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0,255,0),
                2)

    cv2.putText(frame,
                f"Piezo : {piezo}",
                (20,70),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255,255,0),
                2)

    cv2.putText(frame,
                f"IR : {'Detected' if ir else 'No Object'}",
                (20,105),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0,255,255),
                2)

    cv2.putText(frame,
                f"SW420 : {'Vibration' if sw else 'Normal'}",
                (20,140),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255,0,255),
                2)

    # -------------------------
    # Crowd Level
    # -------------------------

    if people <= 2:
        status = "LOW"
        color = (0,255,0)

    elif people <=5:
        status = "MEDIUM"
        color = (0,255,255)

    else:
        status = "HIGH"
        color = (0,0,255)

    cv2.putText(frame,
                f"Crowd : {status}",
                (20,180),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                color,
                3)

    cv2.imshow("Crowd Surveillance",frame)

    if cv2.waitKey(1)==ord("q"):
        break

cap.release()
ser.close()
cv2.destroyAllWindows()