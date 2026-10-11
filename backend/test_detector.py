from camera import Camera
from detector import CrowdDetector

import cv2

camera = Camera()

detector = CrowdDetector()

while True:

    frame = camera.read()

    if frame is None:
        break

    people = detector.detect(frame)

    frame = detector.draw(frame,people)

    cv2.putText(

        frame,

        f"People : {detector.count(people)}",

        (20,40),

        cv2.FONT_HERSHEY_SIMPLEX,

        1,

        (0,255,0),

        2

    )

    cv2.imshow("Crowd Detection",frame)

    if cv2.waitKey(1)==ord("q"):
        break

camera.release()

cv2.destroyAllWindows()