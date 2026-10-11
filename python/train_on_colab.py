# ============================================================
# 🧠 HEAD DETECTION MODEL TRAINING — Google Colab Version
# ============================================================
# 
# HOW TO USE (FREE GPU Training):
# 
# 1. Go to https://colab.research.google.com
# 2. Click File → Upload Notebook → Upload this .py file
#    (OR create a new notebook and copy-paste each section)
# 3. Click Runtime → Change Runtime Type → GPU (T4)
# 4. Run each cell in order
#
# This trains on Google's FREE GPU — much faster than local!
# Training will take ~30-60 minutes on Colab GPU.
# ============================================================


# ======================= CELL 1 =======================
# Install required packages

# !pip install ultralytics roboflow -q


# ======================= CELL 2 =======================
# Download Head Detection Dataset from Roboflow
#
# GET YOUR FREE API KEY:
# 1. Go to https://app.roboflow.com (sign up free with Google)
# 2. Settings → API Key → Copy

# from roboflow import Roboflow
#
# rf = Roboflow(api_key="YOUR_API_KEY")  # <-- PASTE KEY HERE
#
# # Search for a head detection dataset on universe.roboflow.com
# # and replace workspace/project/version below:
# project = rf.workspace("WORKSPACE_NAME").project("PROJECT_NAME")
# version = project.version(1)
# dataset = version.download("yolov8")


# ======================= CELL 3 =======================
# Train YOLOv8s on Head Detection

# from ultralytics import YOLO
#
# model = YOLO("yolov8s.pt")
#
# results = model.train(
#     data="/content/dataset/data.yaml",  # Update path after download
#     epochs=80,
#     imgsz=640,
#     batch=16,
#     device="0",
#     lr0=0.01,
#     lrf=0.001,
#     mosaic=1.0,
#     mixup=0.15,
#     degrees=10.0,
#     scale=0.5,
#     fliplr=0.5,
#     project="runs/detect",
#     name="crowd_head_detector",
#     patience=20,
#     plots=True,
#     verbose=True,
# )


# ======================= CELL 4 =======================
# Validate the trained model

# model = YOLO("runs/detect/crowd_head_detector/weights/best.pt")
# results = model.val()
# print(f"mAP50: {results.box.map50:.4f}")
# print(f"Precision: {results.box.mp:.4f}")
# print(f"Recall: {results.box.mr:.4f}")


# ======================= CELL 5 =======================
# Download the trained model to your PC

# from google.colab import files
# files.download("runs/detect/crowd_head_detector/weights/best.pt")
#
# # After downloading:
# # 1. Rename best.pt → crowd_head_model.pt
# # 2. Copy to: Crowed_Surveillence/backend/models/crowd_head_model.pt
# # 3. Restart your backend server
# # Done! ✅
