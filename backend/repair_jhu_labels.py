from pathlib import Path
from PIL import Image

DATASET = Path(r"F:\Crowed_Surveillence\backend\CrowdDatasetJHU")

fixed = 0
unchanged = 0
empty = 0

for split in ["train", "val", "test"]:

    image_dir = DATASET / "images" / split
    label_dir = DATASET / "labels" / split

    print()
    print("=" * 60)
    print(f"Repairing: {split}")
    print("=" * 60)

    for label_path in label_dir.glob("*.txt"):

        image_path = image_dir / f"{label_path.stem}.jpg"

        if not image_path.exists():
            print(f"Missing image: {image_path.name}")
            continue

        with Image.open(image_path) as img:
            W, H = img.size

        new_lines = []
        changed = False

        with open(label_path, "r", encoding="utf-8") as f:

            for line in f:

                parts = line.strip().split()

                if len(parts) != 5:
                    continue

                cls = parts[0]

                cx = float(parts[1])
                cy = float(parts[2])
                bw = float(parts[3])
                bh = float(parts[4])

                # YOLO normalized -> pixels
                x1 = (cx - bw / 2) * W
                y1 = (cy - bh / 2) * H
                x2 = (cx + bw / 2) * W
                y2 = (cy + bh / 2) * H

                old = (x1, y1, x2, y2)

                # Clip bounding box to image boundaries
                x1 = max(0, min(W, x1))
                y1 = max(0, min(H, y1))
                x2 = max(0, min(W, x2))
                y2 = max(0, min(H, y2))

                # Skip invalid/zero-size boxes
                if x2 <= x1 or y2 <= y1:
                    continue

                # Pixel -> YOLO normalized
                new_cx = ((x1 + x2) / 2) / W
                new_cy = ((y1 + y2) / 2) / H
                new_bw = (x2 - x1) / W
                new_bh = (y2 - y1) / H

                if old != (x1, y1, x2, y2):
                    changed = True

                new_lines.append(
                    f"{cls} "
                    f"{new_cx:.6f} "
                    f"{new_cy:.6f} "
                    f"{new_bw:.6f} "
                    f"{new_bh:.6f}"
                )

        with open(label_path, "w", encoding="utf-8") as f:
            f.write("\n".join(new_lines))

        if changed:
            fixed += 1
        else:
            unchanged += 1

print()
print("=" * 60)
print("JHU LABEL REPAIR COMPLETE")
print("=" * 60)
print(f"Files repaired : {fixed}")
print(f"Files unchanged: {unchanged}")
print(f"Dataset        : {DATASET}")