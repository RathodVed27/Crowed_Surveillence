from PIL import Image, ImageDraw
from pathlib import Path

# Paths
image_dir = Path(r"F:\Crowed_Surveillence\backend\CrowdDatasetTiled\images\train")
label_dir = Path(r"F:\Crowed_Surveillence\backend\CrowdDatasetTiled\labels\train")

output_path = Path(r"F:\Crowed_Surveillence\tile_check.jpg")

# Get first tile
images = sorted(image_dir.glob("*.jpg"))

if not images:
    raise FileNotFoundError("No tiled images found.")

image_path = images[0]

# Matching label
label_path = label_dir / f"{image_path.stem}.txt"

print("Image:", image_path)
print("Label:", label_path)

if not label_path.exists():
    raise FileNotFoundError(f"Label not found: {label_path}")

# Open image
image = Image.open(image_path).convert("RGB")
draw = ImageDraw.Draw(image)

width, height = image.size

# Read labels
with open(label_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

count = 0

for line in lines:

    parts = line.strip().split()

    if len(parts) != 5:
        continue

    class_id, xc, yc, w, h = map(float, parts)

    # YOLO normalized -> pixel coordinates
    x_center = xc * width
    y_center = yc * height

    box_width = w * width
    box_height = h * height

    x1 = x_center - box_width / 2
    y1 = y_center - box_height / 2

    x2 = x_center + box_width / 2
    y2 = y_center + box_height / 2

    draw.rectangle(
        [x1, y1, x2, y2],
        outline="red",
        width=2
    )

    count += 1

# Save
image.save(output_path)

print()
print("========================================")
print("TILE LABEL CHECK COMPLETE")
print("========================================")

print(f"Tile size : {width} x {height}")
print(f"Labels    : {count}")
print(f"Saved to  : {output_path}")
print("========================================")