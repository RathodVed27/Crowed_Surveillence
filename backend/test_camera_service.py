import cv2

from services.camera_service import CameraService

camera = CameraService()

camera.start()

print(camera.get_info())

while True:

    frame = camera.get_frame()

    if frame is None:
        break

    cv2.imshow("Camera Service", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

camera.stop()