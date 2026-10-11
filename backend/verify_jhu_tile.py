from pathlib import Path
from PIL import Image, ImageDraw

DATASET = Path(
    r"F:\Crowed_Surveillence\backend\CrowdDatasetJHUTiled"
)

IMAGE = DATASET / "images" / "train" / "0001_tile_0000.jpg"
LABEL = DATASET / "labels" / "train" / "0001_tile_0000.txt"

OUTPUT = Path(
    r"F:\Crowed_Surveillence\backend\jhu_tile_preview.jpg"
)

img = Image.open(IMAGE).convert("RGB")
draw = ImageDraw.Draw(img)

W, H = img.size

count = 0

with open(LABEL, "r", encoding="utf-8") as f:

    for line in f:

        parts = line.strip().split()

        if len(parts) != 5:
            continue

        cls = int(parts[0])

        cx = float(parts[1]) * W
        cy = float(parts[2]) * H
        bw = float(parts[3]) * W
        bh = float(parts[4]) * H

        x1 = cx - bw / 2
        y1 = cy - bh / 2
        x2 = cx + bw / 2
        y2 = cy + bh / 2

        draw.rectangle(
            [x1, y1, x2, y2],
            outline="red",
            width=2
        )

        count += 1

img.save(OUTPUT, quality=95)

print("Tile:", IMAGE)
print("Boxes:", count)
print("Preview:", OUTPUT)