import cv2

from camera import Camera
from tracker import CrowdTracker

camera = Camera()
tracker = CrowdTracker()

while True:

    frame = camera.read()

    if frame is None:
        break

    results = tracker.track(frame)

    people = tracker.get_people(results)

    output = tracker.draw(frame.copy(), people)

    cv2.putText(
        output,
        f"People: {tracker.count(people)}",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 255),
        2
    )

    cv2.imshow("Crowd Tracker", output)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

camera.release()
cv2.destroyAllWindows()