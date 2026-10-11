import os
import shutil
from scipy.io import loadmat
import cv2

# -------------------------------------------------------
# ShanghaiTech dataset path
# -------------------------------------------------------

DATASET_ROOT = r"C:\Users\hp\Desktop\Crowed Density\Sanghai DataSet\ShanghaiTech"

# -------------------------------------------------------
# Output dataset path
# -------------------------------------------------------

OUTPUT_ROOT = r"C:\Users\hp\Desktop\Crowed_Surveillence\backend\CrowdDataset"

BOX_SIZE = 18  # head box size in pixels


def convert_split(part_name, split_name):
    image_folder = os.path.join(
        DATASET_ROOT,
        part_name,
        split_name,
        "images"
    )

    gt_folder = os.path.join(
        DATASET_ROOT,
        part_name,
        split_name,
        "ground-truth"
    )

    if split_name == "train_data":
        image_out = os.path.join(
            OUTPUT_ROOT,
            "images",
            "train"
        )

        label_out = os.path.join(
            OUTPUT_ROOT,
            "labels",
            "train"
        )
    else:
        image_out = os.path.join(
            OUTPUT_ROOT,
            "images",
            "val"
        )

        label_out = os.path.join(
            OUTPUT_ROOT,
            "labels",
            "val"
        )

    os.makedirs(image_out, exist_ok=True)
    os.makedirs(label_out, exist_ok=True)

    image_files = [
        f for f in os.listdir(image_folder)
        if f.endswith(".jpg")
    ]

    print(f"Converting {part_name} {split_name}...")

    for image_name in image_files:
        image_path = os.path.join(
            image_folder,
            image_name
        )

        mat_name = "GT_" + os.path.splitext(image_name)[0] + ".mat"

        mat_path = os.path.join(
            gt_folder,
            mat_name
        )

        image = cv2.imread(image_path)

        if image is None:
            continue

        h, w = image.shape[:2]

        if not os.path.exists(mat_path):
            print(f"Skipping: {image_name} (annotation not found)")
            continue

        mat = loadmat(mat_path)

        points = mat["image_info"][0][0][0][0][0]

        label_name = os.path.splitext(image_name)[0] + ".txt"

        label_path = os.path.join(
            label_out,
            label_name
        )

        with open(label_path, "w") as f:
            for p in points:
                x = float(p[0])
                y = float(p[1])

                bw = BOX_SIZE / w
                bh = BOX_SIZE / h
                xc = x / w
                yc = y / h

                if 0 <= xc <= 1 and 0 <= yc <= 1:
                    f.write(
                        f"0 {xc:.6f} {yc:.6f} {bw:.6f} {bh:.6f}\n"
                    )

        shutil.copy2(
            image_path,
            os.path.join(image_out, image_name)
        )

    print(f"Finished {part_name} {split_name}")


if __name__ == "__main__":
    convert_split("part_A", "train_data")
    convert_split("part_A", "test_data")
    convert_split("part_B", "train_data")
    convert_split("part_B", "test_data")

    print("YOLO dataset created successfully!")