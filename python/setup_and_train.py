"""
setup_and_train.py
----------------------------------------------------
ONE-CLICK Setup: Downloads dataset + Trains model
for accurate head detection in dense crowds.
----------------------------------------------------
Author : Ved Rathod
Usage  : python setup_and_train.py
----------------------------------------------------

This script does EVERYTHING automatically:
  Step 1: Installs required packages (roboflow)
  Step 2: Downloads a head detection dataset from Roboflow
  Step 3: Organizes dataset into correct folder structure
  Step 4: Trains YOLOv8s model on head detection
  Step 5: Deploys the trained model to backend

BEFORE RUNNING:
  You need a FREE Roboflow API key:
  1. Go to https://app.roboflow.com  (Sign up FREE with Google)
  2. Go to Settings → API Key → Copy your key
  3. Paste it below in ROBOFLOW_API_KEY
"""

import os
import sys
import shutil
from pathlib import Path

# ============================================================
#  ⚠️  PASTE YOUR ROBOFLOW API KEY HERE  ⚠️
# ============================================================
# Get your FREE key from: https://app.roboflow.com/settings
# Sign up with Google → Settings → API Key → Copy

ROBOFLOW_API_KEY = "QvfxI4H9FwwsEZjpTg2E"   # <-- PASTE YOUR KEY HERE (e.g., "abc123xyz")

# ============================================================
#  PATHS
# ============================================================

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATASET_DIR = PROJECT_DIR / "dataset"
BACKEND_DIR = PROJECT_DIR / "backend"
MODEL_DEPLOY_PATH = BACKEND_DIR / "models" / "crowd_head_model.pt"

# ============================================================
#  STEP 1: Install Roboflow
# ============================================================

def install_roboflow():
    print()
    print("=" * 60)
    print("  📦 STEP 1: Installing Roboflow package...")
    print("=" * 60)

    os.system(f"{sys.executable} -m pip install roboflow --quiet")
    print("  ✅ Roboflow installed")


# ============================================================
#  STEP 2: Download Dataset
# ============================================================

def download_dataset():
    print()
    print("=" * 60)
    print("  📥 STEP 2: Downloading Head Detection Dataset...")
    print("=" * 60)

    if not ROBOFLOW_API_KEY:
        print()
        print("  ❌ API KEY NOT SET!")
        print()
        print("  How to get your FREE API key:")
        print("  1. Go to https://app.roboflow.com")
        print("  2. Sign up FREE (use Google login)")
        print("  3. Click Settings (gear icon) → API Key")
        print("  4. Copy the key")
        print("  5. Open this file and paste it in ROBOFLOW_API_KEY")
        print()
        sys.exit(1)

    print("  Go to https://universe.roboflow.com")
    print("  Search for 'Head Detection' or 'Crowd Head' and select a dataset.")
    print("  Look at the URL of the dataset you chose.")
    print("  Example URL: https://universe.roboflow.com/john-doe/head-dataset")
    print("  Workspace = john-doe")
    print("  Project = head-dataset")
    print()
    
    workspace = input("  Enter the Workspace Name: ").strip()
    project_name = input("  Enter the Project Name: ").strip()
    
    if not workspace or not project_name:
        print("  ❌ You must provide a workspace and project name.")
        sys.exit(1)

    from roboflow import Roboflow

    rf = Roboflow(api_key=ROBOFLOW_API_KEY)

    try:
        print(f"  Downloading dataset from {workspace}/{project_name}...")
        
        project = rf.workspace(workspace).project(project_name)
        
        # We will try to download version 1, if it fails, try version 2 or 3
        version = None
        for v in range(1, 6):
            try:
                version = project.version(v)
                print(f"  Found version {v}!")
                break
            except:
                pass
                
        if version is None:
             print("  ❌ Could not find a valid dataset version. Try a different dataset.")
             return False

        dataset = version.download(
            "yolov8",
            location=str(DATASET_DIR)
        )
        print("  ✅ Dataset downloaded!")
        return True

    except Exception as e:
        print(f"  ❌ Failed to download dataset: {e}")
        print()
        print("  📋 MANUAL DOWNLOAD NEEDED:")
        print("  1. Go to https://universe.roboflow.com")
        print("  2. Search 'Head Detection'")
        print("  3. Pick dataset with 2000+ images")
        print("  4. Click Download → YOLOv8 format → Download ZIP")
        print("  5. Extract ZIP into: dataset/ folder")
        print(f"     Path: {DATASET_DIR}")
        print()
        return False


# ============================================================
#  STEP 3: Verify & Fix Dataset Structure
# ============================================================

def verify_and_fix_dataset():
    print()
    print("=" * 60)
    print("  🔍 STEP 3: Verifying Dataset Structure...")
    print("=" * 60)

    # Check if data.yaml exists
    yaml_path = DATASET_DIR / "data.yaml"

    if not yaml_path.exists():
        # Look for it in subdirectories
        for p in DATASET_DIR.rglob("data.yaml"):
            yaml_path = p
            break

    if not yaml_path.exists():
        print("  ❌ data.yaml not found!")
        return False

    # Read and fix paths in data.yaml
    content = yaml_path.read_text()

    # Update paths to absolute
    new_content = []
    for line in content.splitlines():
        if line.strip().startswith("train:"):
            train_path = DATASET_DIR / "train" / "images"
            if not train_path.exists():
                # Check for alternative structure
                for alt in ["train/images", "train"]:
                    alt_path = DATASET_DIR / alt
                    if alt_path.exists():
                        train_path = alt_path
                        break
            new_content.append(f"train: {str(train_path).replace(chr(92), '/')}")

        elif line.strip().startswith("val:") or line.strip().startswith("valid:"):
            valid_path = DATASET_DIR / "valid" / "images"
            if not valid_path.exists():
                for alt in ["val/images", "valid/images", "val", "valid"]:
                    alt_path = DATASET_DIR / alt
                    if alt_path.exists():
                        valid_path = alt_path
                        break
            new_content.append(f"val: {str(valid_path).replace(chr(92), '/')}")

        elif line.strip().startswith("test:"):
            test_path = DATASET_DIR / "test" / "images"
            if not test_path.exists():
                for alt in ["test/images", "test"]:
                    alt_path = DATASET_DIR / alt
                    if alt_path.exists():
                        test_path = alt_path
                        break
            new_content.append(f"test: {str(test_path).replace(chr(92), '/')}")
        else:
            new_content.append(line)

    yaml_path.write_text("\n".join(new_content))

    # Count images
    train_count = 0
    valid_count = 0

    for split_name in ["train"]:
        img_dir = DATASET_DIR / split_name / "images"
        if img_dir.exists():
            train_count = len(list(img_dir.glob("*.*")))

    for split_name in ["valid", "val"]:
        img_dir = DATASET_DIR / split_name / "images"
        if img_dir.exists():
            valid_count = len(list(img_dir.glob("*.*")))

    print(f"  Training images:   {train_count}")
    print(f"  Validation images: {valid_count}")
    print(f"  data.yaml:         ✅ Updated with absolute paths")

    if train_count == 0:
        print("  ❌ No training images found!")
        return False

    print("  ✅ Dataset verified!")
    return True


# ============================================================
#  STEP 4: Train Model
# ============================================================

def train_model():
    print()
    print("=" * 60)
    print("  🧠 STEP 4: Training YOLOv8s Head Detection Model...")
    print("=" * 60)
    print()
    print("  Base Model: YOLOv8s (Small — balanced speed & accuracy)")
    print("  Epochs: 80")
    print("  Device: NVIDIA GPU (CUDA)")
    print("  Estimated Time: 1-2 hours")
    print()

    from ultralytics import YOLO

    # Find data.yaml
    yaml_path = DATASET_DIR / "data.yaml"
    if not yaml_path.exists():
        for p in DATASET_DIR.rglob("data.yaml"):
            yaml_path = p
            break

    model = YOLO("yolov8s.pt")

    results = model.train(
        # Dataset
        data=str(yaml_path),

        # Training
        epochs=80,
        imgsz=640,
        batch=16,           # Reduce to 8 if out of memory
        device="0",         # NVIDIA GPU

        # Learning rate
        lr0=0.01,
        lrf=0.001,

        # Augmentation (helps detect small/dense heads)
        mosaic=1.0,
        mixup=0.15,
        degrees=10.0,
        scale=0.5,
        flipud=0.0,
        fliplr=0.5,
        hsv_h=0.015,
        hsv_s=0.7,
        hsv_v=0.4,

        # Output
        project="runs/detect",
        name="crowd_head_detector",
        exist_ok=True,

        # Save
        save=True,
        save_period=10,

        # Early stopping
        patience=20,

        # Workers
        workers=4,

        # Plots
        plots=True,
        verbose=True,
    )

    print()
    print("  ✅ Training Complete!")
    return True


# ============================================================
#  STEP 5: Deploy Trained Model
# ============================================================

def deploy_model():
    print()
    print("=" * 60)
    print("  🚀 STEP 5: Deploying Trained Model...")
    print("=" * 60)

    # Find the best model
    best_model = Path("runs/detect/crowd_head_detector/weights/best.pt")

    if not best_model.exists():
        # Search for it
        for p in Path("runs").rglob("best.pt"):
            best_model = p
            break

    if not best_model.exists():
        print("  ❌ Trained model not found!")
        return False

    # Copy to backend
    MODEL_DEPLOY_PATH.parent.mkdir(parents=True, exist_ok=True)

    if MODEL_DEPLOY_PATH.exists():
        backup = MODEL_DEPLOY_PATH.with_suffix(".pt.backup")
        shutil.copy2(MODEL_DEPLOY_PATH, backup)
        print(f"  Backed up old model → {backup.name}")

    shutil.copy2(best_model, MODEL_DEPLOY_PATH)

    size_mb = MODEL_DEPLOY_PATH.stat().st_size / (1024 * 1024)
    print(f"  ✅ Model deployed: {MODEL_DEPLOY_PATH.name} ({size_mb:.1f} MB)")
    print()
    print("  🎉 ALL DONE! Restart your backend server.")
    print("     The system will automatically use the new model.")

    return True


# ============================================================
#  MAIN
# ============================================================

if __name__ == "__main__":

    print()
    print("╔══════════════════════════════════════════════════════╗")
    print("║  🧠 HEAD DETECTION MODEL — AUTOMATED TRAINING      ║")
    print("║  For Crowd Surveillance System                      ║")
    print("║  Author: Ved Rathod                                 ║")
    print("╚══════════════════════════════════════════════════════╝")

    # Step 1: Install packages
    install_roboflow()

    # Step 2: Download dataset
    success = download_dataset()
    if not success:
        print("\n  ⚠️ Download the dataset manually, then re-run this script.")
        sys.exit(1)

    # Step 3: Verify dataset
    success = verify_and_fix_dataset()
    if not success:
        print("\n  ⚠️ Dataset verification failed.")
        sys.exit(1)

    # Step 4: Train model
    train_model()

    # Step 5: Deploy
    deploy_model()

    print()
    print("=" * 60)
    print("  🎉 SETUP COMPLETE!")
    print("  Your model can now detect heads in dense crowds.")
    print("  Restart your backend to use the new model.")
    print("=" * 60)
