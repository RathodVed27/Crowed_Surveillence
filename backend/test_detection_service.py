import cv2

from services.camera_service import CameraService
from services.detection_service import DetectionService

camera = CameraService()
detector = DetectionService()

camera.start()
detector.start()

while True:

    frame = camera.get_frame()

    if frame is None:
        break

    result = detector.process_frame(frame)

    output = result["frame"]

    count = result["count"]

    cv2.putText(

        output,

        f"People : {count}",

        (20,40),

        cv2.FONT_HERSHEY_SIMPLEX,

        1,

        (0,255,255),

        2

    )

    cv2.imshow("Crowd Detection", output)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

camera.stop()
detector.stop()

cv2.destroyAllWindows()