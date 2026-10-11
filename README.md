# AI Crowd Surveillance System 🚀👁️

An end-to-end, real-time AI-powered crowd monitoring and density surveillance system designed for public safety, event monitoring, and enterprise facility analytics.

---

## 🌟 Key Features

- **Real-Time People Detection & Tracking**: Leverages state-of-the-art YOLOv8 architecture and ByteTrack for accurate crowd counting and trajectory tracking.
- **Dynamic Density & Flow Heatmaps**: Identifies congestion hotspots and directional flow patterns.
- **Interactive Web Dashboard**: Modern frontend displaying live CCTV streams, telemetry metrics, alert logs, and statistical charts.
- **Hardware Telemetry Integration**: Reads environment and presence sensors via Arduino serial communication for hybrid IoT-vision intelligence.
- **Alert & Anomaly Engine**: Configurable density thresholds and anomalous movement detection with automated logging and reporting.

---

## 📂 Project Architecture

```plaintext
Crowed_Surveillence/
├── arduino/              # Arduino microcontroller code for physical sensors
├── backend/              # Enterprise Python backend (Flask API, AI pipelines)
│   ├── api/              # RESTful API endpoints & route handlers
│   ├── core/             # Configuration, logging, & core logic
│   ├── database/         # Data persistence & telemetry logging
│   ├── evaluation/       # Performance evaluation scripts
│   ├── models/           # Model definitions and inference runners
│   ├── repositories/     # Data access layer
│   ├── services/         # Detection, tracking, & alert services
│   └── trackers/         # Multi-object tracking (ByteTrack)
├── frontend/             # Real-time web monitoring interface
│   ├── assets/           # CSS, icons, and JavaScript charting modules
│   └── index.html        # Main surveillance dashboard
├── live_detection.py     # Standalone live camera detection runner
├── live_tracking.py      # Standalone multi-object tracking runner
├── sensor_reader.py      # Serial interface reader for IoT sensors
└── requirements.txt      # Python dependencies
```

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.9+ installed
- CUDA-compatible GPU (recommended for real-time high-FPS inference)
- Web browser (Chrome / Edge / Firefox)

### 2. Setup Virtual Environment

```bash
# Clone the repository
git clone https://github.com/RathodVed27/Crowed_Surveillence.git
cd Crowed_Surveillence

# Create and activate virtual environment
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Model Weights
Download or place your trained YOLO weights (e.g., `yolov8n.pt` / `yolov8m.pt`) in the root or `backend/models/` folder. YOLO will automatically download default weights on first execution if not found locally.

### 4. Running the Application

- **Live Detection Pipeline:**
  ```bash
  python live_detection.py
  ```

- **Live Tracking & Counting:**
  ```bash
  python live_tracking.py
  ```

- **Backend API & Surveillance Server:**
  ```bash
  python backend/api/server.py
  ```

- **Dashboard:**
  Open `frontend/index.html` in your web browser.

---

## 🛠️ Tech Stack

- **Computer Vision & AI**: Ultralytics YOLOv8, OpenCV, ByteTrack, PyTorch
- **Backend**: Flask, Waitress, Python 3.x
- **Frontend**: Modern Vanilla JS, HTML5, CSS3, Chart.js
- **IoT & Sensors**: Arduino, PySerial

---

## 📜 License
This project is open-source and available under the [MIT License](LICENSE).
