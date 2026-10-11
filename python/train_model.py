"""
train_model.py
----------------------------------------------------
Fine-tune YOLOv8s on Head Detection Dataset
for accurate crowd counting in dense scenes.
----------------------------------------------------
Author : Ved Rathod
Usage  : python train_model.py
----------------------------------------------------

This script fine-tunes a YOLOv8s model to detect human
heads instead of full bodies. Head detection is far
more accurate in dense crowds where bodies are occluded
and only the top of heads are visible.

After training completes, the best model will be saved at:
  runs/detect/crowd_head_detector/weights/best.pt

Copy that file to:
  backend/models/crowd_head_model.pt

Then update backend/config.py to point to the new model.
"""

import sys
from pathlib import Path
from ultralytics import YOLO

# --------------------------------------------------------
# CONFIGURATION — Adjust these settings as needed
# --------------------------------------------------------

# Base model to fine-tune (yolov8s = small, good balance)
BASE_MODEL = "yolov8s.pt"

# Path to the dataset configuration
DATASET_YAML = str(Path(__file__).resolve().parent.parent / "dataset" / "data.yaml")

# Training hyperparameters
EPOCHS = 100            # Number of training epochs (100 is a good starting point)
IMAGE_SIZE = 640        # Image resolution for training
BATCH_SIZE = 16         # Reduce to 8 if you get CUDA out of memory errors
DEVICE = "0"            # "0" = first NVIDIA GPU, "cpu" = CPU only

# Learning rate (slightly lower for fine-tuning)
LR0 = 0.01             # Initial learning rate
LRF = 0.001            # Final learning rate

# Data augmentation (helps with crowd variety)
MOSAIC = 1.0            # Mosaic augmentation (combines 4 images)
MIXUP = 0.1             # MixUp augmentation (blends 2 images)
DEGREES = 10.0          # Random rotation ±10 degrees
SCALE = 0.5             # Random scale ±50%
FLIPUD = 0.5            # Vertical flip probability
FLIPLR = 0.5            # Horizontal flip probability

# Output
PROJECT_NAME = "runs/detect"
RUN_NAME = "crowd_head_detector"

# --------------------------------------------------------
# PRE-FLIGHT CHECKS
# --------------------------------------------------------

def preflight_checks():
    """Verify everything is ready before training."""

    print()
    print("=" * 60)
    print("  🧠 YOLOv8 HEAD DETECTION — TRAINING SETUP")
    print("=" * 60)

    # Check dataset
    dataset_path = Path(DATASET_YAML)
    if not dataset_path.exists():
        print(f"  ❌ Dataset config not found: {DATASET_YAML}")
        print(f"     Run download_dataset.py first!")
        sys.exit(1)

    print(f"  ✅ Dataset config: {dataset_path.name}")

    # Check training images exist
    dataset_dir = dataset_path.parent
    train_images = dataset_dir / "train" / "images"

    if train_images.exists():
        count = len(list(train_images.glob("*.*")))
        if count == 0:
            print(f"  ❌ No training images found in {train_images}")
            print(f"     Download a dataset first!")
            sys.exit(1)
        print(f"  ✅ Training images: {count}")
    else:
        print(f"  ❌ Training images folder missing: {train_images}")
        sys.exit(1)

    # Check validation images
    valid_images = dataset_dir / "valid" / "images"
    if valid_images.exists():
        count = len(list(valid_images.glob("*.*")))
        print(f"  ✅ Validation images: {count}")
    else:
        print(f"  ⚠️  No validation folder found (training will still work)")

    # Check GPU
    try:
        import torch
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            gpu_mem = torch.cuda.get_device_properties(0).total_mem / (1024**3)
            print(f"  ✅ GPU: {gpu_name} ({gpu_mem:.1f} GB)")
        else:
            print(f"  ⚠️  No NVIDIA GPU detected — training will be SLOW on CPU")
            print(f"     Consider using Google Colab for faster training")
    except ImportError:
        print(f"  ⚠️  PyTorch not installed — run: pip install torch torchvision")

    print(f"  📦 Base Model: {BASE_MODEL}")
    print(f"  🔄 Epochs: {EPOCHS}")
    print(f"  📐 Image Size: {IMAGE_SIZE}")
    print(f"  📦 Batch Size: {BATCH_SIZE}")
    print(f"  🎯 Device: {'GPU' if DEVICE != 'cpu' else 'CPU'}")
    print("=" * 60)
    print()


# --------------------------------------------------------
# TRAIN
# --------------------------------------------------------

def train():
    """Run the training pipeline."""

    preflight_checks()

    print("Loading base model...")
    model = YOLO(BASE_MODEL)

    print("Starting training...")
    print("(This may take 1-3 hours on GPU, 8-12 hours on CPU)")
    print()

    results = model.train(

        # Dataset
        data=DATASET_YAML,

        # Training duration
        epochs=EPOCHS,

        # Image settings
        imgsz=IMAGE_SIZE,

        # Batch size (reduce if out of memory)
        batch=BATCH_SIZE,

        # Device
        device=DEVICE,

        # Learning rate schedule
        lr0=LR0,
        lrf=LRF,

        # Data augmentation for crowd diversity
        mosaic=MOSAIC,
        mixup=MIXUP,
        degrees=DEGREES,
        scale=SCALE,
        flipud=FLIPUD,
        fliplr=FLIPLR,

        # Output location
        project=PROJECT_NAME,
        name=RUN_NAME,

        # Save settings
        save=True,
        save_period=10,         # Save checkpoint every 10 epochs

        # Performance
        workers=4,              # Data loader workers
        patience=20,            # Early stopping: stop if no improvement for 20 epochs

        # Visualization
        plots=True,             # Generate training plots

        # Resume training if interrupted
        exist_ok=True,

        # Verbose output
        verbose=True,
    )

    print()
    print("=" * 60)
    print("  ✅ TRAINING COMPLETE!")
    print("=" * 60)
    print()
    print(f"  Best model saved at:")
    print(f"    {PROJECT_NAME}/{RUN_NAME}/weights/best.pt")
    print()
    print(f"  Training plots saved at:")
    print(f"    {PROJECT_NAME}/{RUN_NAME}/")
    print()
    print("  NEXT STEPS:")
    print("  1. Copy best.pt to backend/models/crowd_head_model.pt")
    print("  2. The config.py has already been updated to use it")
    print("  3. Restart your backend server")
    print("=" * 60)

    return results


# --------------------------------------------------------
# VALIDATE
# --------------------------------------------------------

def validate():
    """Run validation on the trained model."""

    best_model = Path(PROJECT_NAME) / RUN_NAME / "weights" / "best.pt"

    if not best_model.exists():
        print(f"❌ No trained model found at {best_model}")
        print(f"   Run training first!")
        return

    print(f"Validating model: {best_model}")
    model = YOLO(str(best_model))

    results = model.val(
        data=DATASET_YAML,
        imgsz=IMAGE_SIZE,
        batch=BATCH_SIZE,
        device=DEVICE,
    )

    print()
    print("Validation Results:")
    print(f"  mAP50:    {results.box.map50:.4f}")
    print(f"  mAP50-95: {results.box.map:.4f}")
    print(f"  Precision: {results.box.mp:.4f}")
    print(f"  Recall:    {results.box.mr:.4f}")

    return results


# --------------------------------------------------------
# Main
# --------------------------------------------------------

if __name__ == "__main__":

    if len(sys.argv) > 1 and sys.argv[1] == "validate":
        validate()
    else:
        train()
