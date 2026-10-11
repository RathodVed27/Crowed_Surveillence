import cv2

from services.camera_service import CameraService
from services.tracking_service import TrackingService

camera = CameraService()
tracker = TrackingService()

camera.start()
tracker.start()

while True:

    frame = camera.get_frame()

    if frame is None:
        break

    result = tracker.process_frame(frame)

    frame = result["frame"]

    cv2.putText(
        frame,
        f"People : {result['count']}",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 255),
        2
    )

    cv2.putText(
    frame,
    f"Occupancy : {result['occupancy']}",
    (20,80),
    cv2.FONT_HERSHEY_SIMPLEX,
    1,
    (255,255,0),
    2
)

    cv2.imshow("Tracking Service", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

camera.stop()
tracker.stop()

cv2.destroyAllWindows()