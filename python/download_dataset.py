"""
download_dataset.py
----------------------------------------------------
Downloads a Head Detection dataset from Roboflow
for training YOLOv8 to detect heads in dense crowds.
----------------------------------------------------
Author : Ved Rathod
Usage  : python download_dataset.py
----------------------------------------------------

This script downloads a curated head-detection dataset
and organizes it into the correct folder structure for
YOLOv8 training.

You have TWO options:

  OPTION A (Recommended) — Roboflow API (automatic download)
    1. Go to https://universe.roboflow.com
    2. Search for "Head Detection" or "Crowd Head Detection"
    3. Pick a dataset with 2000+ images
    4. Click "Download Dataset" → choose "YOLOv8" format
    5. Copy the API download code and paste it below

  OPTION B — Manual download
    1. Download a dataset ZIP from Roboflow / Kaggle in YOLOv8 format
    2. Extract it so the structure looks like:
       dataset/
         train/images/  train/labels/
         valid/images/  valid/labels/
         test/images/   test/labels/
         data.yaml
"""

import os
import sys
import shutil
from pathlib import Path

# --------------------------------------------------------
# CONFIGURATION
# --------------------------------------------------------

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATASET_DIR = PROJECT_DIR / "dataset"

# --------------------------------------------------------
# OPTION A: Roboflow API Download (RECOMMENDED)
# --------------------------------------------------------
# To use this:
# 1. pip install roboflow
# 2. Get your API key from https://app.roboflow.com/settings
# 3. Fill in the details below
# --------------------------------------------------------

ROBOFLOW_API_KEY = ""          # <-- Paste your API key here
ROBOFLOW_WORKSPACE = ""         # <-- e.g., "your-workspace"
ROBOFLOW_PROJECT = ""           # <-- e.g., "head-detection-xxxxx"
ROBOFLOW_VERSION = 1            # <-- Dataset version number


def download_from_roboflow():
    """Download dataset automatically from Roboflow."""

    if not ROBOFLOW_API_KEY:
        print("=" * 60)
        print("  ROBOFLOW API KEY NOT SET!")
        print("=" * 60)
        print()
        print("  To download automatically:")
        print("  1. Go to https://universe.roboflow.com")
        print("  2. Search for 'Head Detection'")
        print("  3. Pick a dataset (look for 2000+ images)")
        print("  4. Click 'Download Dataset' → YOLOv8 format")
        print("  5. Copy the API key and project details")
        print("  6. Paste them at the top of this script")
        print()
        print("  OR use OPTION B: Download the ZIP manually")
        print("  and extract into the dataset/ folder.")
        print("=" * 60)
        return False

    try:
        from roboflow import Roboflow
    except ImportError:
        print("Installing roboflow...")
        os.system(f"{sys.executable} -m pip install roboflow")
        from roboflow import Roboflow

    print(f"Connecting to Roboflow...")
    rf = Roboflow(api_key=ROBOFLOW_API_KEY)

    project = rf.workspace(ROBOFLOW_WORKSPACE).project(ROBOFLOW_PROJECT)
    version = project.version(ROBOFLOW_VERSION)

    print(f"Downloading dataset: {ROBOFLOW_PROJECT} v{ROBOFLOW_VERSION}")
    download = version.download("yolov8", location=str(DATASET_DIR))

    print(f"Dataset downloaded to: {DATASET_DIR}")
    return True


# --------------------------------------------------------
# OPTION B: Organize a manually downloaded ZIP
# --------------------------------------------------------

def organize_manual_download(zip_path: str):
    """
    Extract and organize a manually downloaded dataset ZIP.

    Usage:
        python download_dataset.py path/to/dataset.zip
    """

    import zipfile

    zip_path = Path(zip_path)

    if not zip_path.exists():
        print(f"ERROR: File not found: {zip_path}")
        return False

    print(f"Extracting {zip_path}...")

    # Extract to a temporary folder first
    temp_dir = DATASET_DIR / "_temp_extract"
    temp_dir.mkdir(exist_ok=True)

    with zipfile.ZipFile(zip_path, 'r') as z:
        z.extractall(temp_dir)

    # Find the extracted content (might be nested in a folder)
    extracted_items = list(temp_dir.iterdir())

    # If there's a single subfolder, go into it
    if len(extracted_items) == 1 and extracted_items[0].is_dir():
        source_dir = extracted_items[0]
    else:
        source_dir = temp_dir

    # Move files into the correct structure
    for split in ["train", "valid", "val", "test"]:

        src_images = source_dir / split / "images"
        src_labels = source_dir / split / "labels"

        # Normalize "val" to "valid"
        dest_split = "valid" if split == "val" else split

        dest_images = DATASET_DIR / dest_split / "images"
        dest_labels = DATASET_DIR / dest_split / "labels"

        dest_images.mkdir(parents=True, exist_ok=True)
        dest_labels.mkdir(parents=True, exist_ok=True)

        if src_images.exists():
            for f in src_images.iterdir():
                shutil.copy2(f, dest_images / f.name)
            print(f"  Copied {len(list(src_images.iterdir()))} images → {dest_split}/images/")

        if src_labels.exists():
            for f in src_labels.iterdir():
                shutil.copy2(f, dest_labels / f.name)
            print(f"  Copied {len(list(src_labels.iterdir()))} labels → {dest_split}/labels/")

    # Copy data.yaml if present
    for yaml_file in source_dir.glob("*.yaml"):
        shutil.copy2(yaml_file, DATASET_DIR / "data.yaml")
        print(f"  Copied {yaml_file.name} → data.yaml")

    # Clean up temp folder
    shutil.rmtree(temp_dir)

    print("Dataset organized successfully!")
    return True


# --------------------------------------------------------
# Verify Dataset
# --------------------------------------------------------

def verify_dataset():
    """Check that the dataset is properly structured."""

    print()
    print("=" * 60)
    print("  DATASET VERIFICATION")
    print("=" * 60)

    all_good = True

    for split in ["train", "valid"]:

        img_dir = DATASET_DIR / split / "images"
        lbl_dir = DATASET_DIR / split / "labels"

        if img_dir.exists():
            img_count = len(list(img_dir.glob("*.*")))
        else:
            img_count = 0

        if lbl_dir.exists():
            lbl_count = len(list(lbl_dir.glob("*.txt")))
        else:
            lbl_count = 0

        status = "OK" if img_count > 0 and lbl_count > 0 else "EMPTY"

        if status == "EMPTY":
            all_good = False

        print(f"  {split:8s} → {img_count:5d} images, {lbl_count:5d} labels  [{status}]")

    yaml_path = DATASET_DIR / "data.yaml"
    yaml_ok = yaml_path.exists()

    print(f"  data.yaml → {'FOUND' if yaml_ok else 'MISSING'}")

    if not yaml_ok:
        all_good = False

    print()

    if all_good:
        print("  ✅ Dataset is ready for training!")
        print(f"     Run: python train_model.py")
    else:
        print("  ❌ Dataset is incomplete.")
        print("     Please download images and labels first.")
        print()
        print("  QUICK START:")
        print("  1. Go to https://universe.roboflow.com")
        print("  2. Search 'Head Detection'")
        print("  3. Download in YOLOv8 format (ZIP)")
        print("  4. Run: python download_dataset.py path/to/dataset.zip")

    print("=" * 60)
    return all_good


# --------------------------------------------------------
# Main
# --------------------------------------------------------

if __name__ == "__main__":

    print()
    print("🧠 Head Detection Dataset Downloader")
    print("   For Crowd Surveillance System")
    print()

    if len(sys.argv) > 1:
        # Manual ZIP extraction mode
        zip_path = sys.argv[1]
        organize_manual_download(zip_path)
    else:
        # Try Roboflow API download
        download_from_roboflow()

    # Always verify at the end
    verify_dataset()
