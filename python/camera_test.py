from ultralytics import YOLO
import cv2

# Load YOLO model
model = YOLO("yolov8n.pt")

# Open Webcam
cap = cv2.VideoCapture(0)

while True:

    ret, frame = cap.read()

    if not ret:
        break

    # Run YOLO
    results = model(frame, verbose=False)

    people_count = 0

    # Detect only people
    for result in results:
        for box in result.boxes:

            cls = int(box.cls[0])

            # Class 0 = Person
            if cls == 0:
                people_count += 1

    # Draw bounding boxes
    annotated = results[0].plot()

    # Display people count
    cv2.putText(
        annotated,
        f"People Count : {people_count}",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2,
    )

    cv2.imshow("Crowd Surveillance", annotated)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()