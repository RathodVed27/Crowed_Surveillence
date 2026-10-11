from pathlib import Path
from PIL import Image, ImageDraw

IMAGE = Path(r"F:\Crowed_Surveillence\backend\CrowdDatasetJHU\images\train\0001.jpg")
LABEL = Path(r"F:\Crowed_Surveillence\backend\CrowdDatasetJHU\labels\train\0001.txt")

OUTPUT = Path(r"F:\Crowed_Surveillence\backend\jhu_preview_0001.jpg")


# Load image
img = Image.open(IMAGE).convert("RGB")
draw = ImageDraw.Draw(img)

image_width, image_height = img.size

print(f"Image size: {image_width} x {image_height}")


# Read YOLO labels
with open(LABEL, "r", encoding="utf-8") as f:

    for line in f:

        parts = line.strip().split()

        if len(parts) != 5:
            continue

        class_id = int(parts[0])
        x_center = float(parts[1])
        y_center = float(parts[2])
        width = float(parts[3])
        height = float(parts[4])

        # YOLO normalized → pixels
        x_center *= image_width
        y_center *= image_height
        width *= image_width
        height *= image_height

        x1 = int(x_center - width / 2)
        y1 = int(y_center - height / 2)
        x2 = int(x_center + width / 2)
        y2 = int(y_center + height / 2)

        draw.rectangle(
            [x1, y1, x2, y2],
            outline="red",
            width=2
        )


img.save(OUTPUT, quality=95)

print()
print("Preview created:")
print(OUTPUT)