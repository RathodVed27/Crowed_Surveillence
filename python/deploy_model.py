"""
deploy_model.py
----------------------------------------------------
Copies the trained model to the backend/models/ folder
so the system automatically starts using it.
----------------------------------------------------
Usage: python deploy_model.py
"""

import shutil
from pathlib import Path

# Paths
PROJECT_DIR = Path(__file__).resolve().parent.parent
TRAINED_MODEL = PROJECT_DIR / "python" / "runs" / "detect" / "crowd_head_detector" / "weights" / "best.pt"
DEPLOY_TARGET = PROJECT_DIR / "backend" / "models" / "crowd_head_model.pt"


def deploy():

    print()
    print("=" * 60)
    print("  🚀 MODEL DEPLOYMENT")
    print("=" * 60)

    if not TRAINED_MODEL.exists():
        print(f"  ❌ Trained model not found at:")
        print(f"     {TRAINED_MODEL}")
        print()
        print(f"  Run train_model.py first!")
        print("=" * 60)
        return False

    # Get file size
    size_mb = TRAINED_MODEL.stat().st_size / (1024 * 1024)

    print(f"  Source:  {TRAINED_MODEL}")
    print(f"  Target:  {DEPLOY_TARGET}")
    print(f"  Size:    {size_mb:.1f} MB")

    # Create backup if target already exists
    if DEPLOY_TARGET.exists():
        backup = DEPLOY_TARGET.with_suffix(".pt.backup")
        shutil.copy2(DEPLOY_TARGET, backup)
        print(f"  Backup:  {backup}")

    # Copy the model
    DEPLOY_TARGET.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(TRAINED_MODEL, DEPLOY_TARGET)

    print()
    print("  ✅ Model deployed successfully!")
    print()
    print("  The system will now automatically use the")
    print("  trained head detection model for crowd counting.")
    print()
    print("  Restart your backend server to load the new model.")
    print("=" * 60)

    return True


if __name__ == "__main__":
    deploy()
