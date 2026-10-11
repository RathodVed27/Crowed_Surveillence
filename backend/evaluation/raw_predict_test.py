from ultralytics import YOLO
import cv2
import os


MODEL_PATH = r"F:\Crowed_Surveillence\runs\crowd_yolov8m_combined_tiled\weights\best.pt"

SOURCE_IMAGE = r"F:\PROJECT DATASET\jhu_crowd_v2.0\jhu_crowd_v2.0\val\images\0007.jpg"

OUTPUT_IMAGE = r"F:\Crowed_Surveillence\runs\raw_test_0007.jpg"

TILE_SIZE = 512
OVERLAP = 128

CONFIDENCE = 0.03
MODEL_IOU = 0.50
MAX_DETECTIONS = 1000


print("Loading model...")

model = YOLO(MODEL_PATH)

print("Model loaded.")


image = cv2.imread(SOURCE_IMAGE)

if image is None:
    raise FileNotFoundError(SOURCE_IMAGE)


height, width = image.shape[:2]

print(
    f"Image size: {width} x {height}"
)


def get_positions(length):

    if length <= TILE_SIZE:
        return [0]

    stride = TILE_SIZE - OVERLAP

    positions = []

    position = 0

    while position + TILE_SIZE < length:

        positions.append(position)

        position += stride

    last_position = length - TILE_SIZE

    if last_position not in positions:
        positions.append(last_position)

    return positions


x_starts = get_positions(width)
y_starts = get_positions(height)


raw_count = 0


for y in y_starts:

    for x in x_starts:

        x2 = min(
            x + TILE_SIZE,
            width
        )

        y2 = min(
            y + TILE_SIZE,
            height
        )

        tile = image[
            y:y2,
            x:x2
        ]

        results = model.predict(
            source=tile,
            conf=CONFIDENCE,
            iou=MODEL_IOU,
            imgsz=TILE_SIZE,
            max_det=MAX_DETECTIONS,
            device=0,
            verbose=False
        )

        result = results[0]

        if result.boxes is None:
            continue

        boxes = (
            result.boxes.xyxy
            .cpu()
            .numpy()
        )

        scores = (
            result.boxes.conf
            .cpu()
            .numpy()
        )

        raw_count += len(boxes)


        for box, score in zip(
            boxes,
            scores
        ):

            bx1, by1, bx2, by2 = box

            bx1 += x
            bx2 += x

            by1 += y
            by2 += y


            bx1 = int(
                max(
                    0,
                    min(width, bx1)
                )
            )

            bx2 = int(
                max(
                    0,
                    min(width, bx2)
                )
            )

            by1 = int(
                max(
                    0,
                    min(height, by1)
                )
            )

            by2 = int(
                max(
                    0,
                    min(height, by2)
                )
            )


            if bx2 <= bx1 or by2 <= by1:
                continue


            cv2.rectangle(
                image,
                (bx1, by1),
                (bx2, by2),
                (0, 255, 0),
                1
            )


            cv2.putText(
                image,
                f"{score:.2f}",
                (
                    bx1,
                    max(
                        12,
                        by1 - 2
                    )
                ),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.30,
                (0, 255, 0),
                1
            )


cv2.putText(
    image,
    f"Raw detections: {raw_count}",
    (20, 40),
    cv2.FONT_HERSHEY_SIMPLEX,
    1,
    (0, 255, 0),
    2
)


os.makedirs(
    os.path.dirname(
        OUTPUT_IMAGE
    ),
    exist_ok=True
)

cv2.imwrite(
    OUTPUT_IMAGE,
    image
)


print()
print("=" * 60)
print(
    f"RAW DETECTIONS: {raw_count}"
)
print(
    f"Output: {OUTPUT_IMAGE}"
)
print("=" * 60)