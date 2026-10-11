"""
shared_services.py
-------------------------------------------------------
Enterprise Shared Service Container (Dependency Injection)
Guarantees a SINGLE shared instance of:
- CameraService
- TrackingService
- SensorService
- AnalyticsService
- AlertService
- HeatmapService
- Database (via repositories)
-------------------------------------------------------
Author : Ved Rathod (Refactored)
"""

import logging
from services.camera_service import CameraService
from services.tracking_service import TrackingService
from services.detection_service import DetectionService
from services.sensor_service import SensorService
from services.analytics_service import AnalyticsService
from services.alert_service import AlertService
from services.heatmap_service import HeatmapService
from models.state import state

logger = logging.getLogger("AI_Surveillance.ServiceContainer")


class ServiceContainer:
    """
    Singleton Service Container.
    All components (Flask API, background worker, analytics engine) access
    services through this single container instance.
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ServiceContainer, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True

        logger.info("Initializing Shared Service Container...")

        # Instantiate single shared services
        self.camera = CameraService()
        self.tracker = TrackingService()
        self.detector = DetectionService()
        self.sensor = SensorService()
        self.analytics = AnalyticsService()
        self.alerts = AlertService()
        self.heatmap = HeatmapService()

        self.started = False
        logger.info("✅ Shared Service Container initialized successfully.")

    def start_all(self):
        """
        Starts all services in the container.
        """
        if self.started:
            logger.info("Services already started.")
            return

        logger.info("Starting all system services...")
        try:
            self.camera.start()
            self.tracker.start()
            self.detector.start()
            self.sensor.start()
            self.heatmap.start()
            self.started = True
            state.update_health_status(camera_connected=True, db_status="ONLINE", ai_status="READY")
            logger.info("✅ All services started successfully.")
        except Exception as e:
            logger.error(f"❌ Error starting services in container: {e}")
            raise

    def stop_all(self):
        """
        Gracefully stops all services in the container.
        """
        if not self.started:
            return

        logger.info("Stopping all system services...")
        try:
            self.camera.stop()
        except Exception as e:
            logger.warning(f"Error stopping CameraService: {e}")

        try:
            self.tracker.stop()
        except Exception as e:
            logger.warning(f"Error stopping TrackingService: {e}")

        try:
            self.detector.stop()
        except Exception as e:
            logger.warning(f"Error stopping DetectionService: {e}")

        try:
            self.sensor.stop()
        except Exception as e:
            logger.warning(f"Error stopping SensorService: {e}")

        try:
            self.analytics.stop()
        except Exception as e:
            logger.warning(f"Error stopping AnalyticsService: {e}")

        try:
            self.alerts.stop()
        except Exception as e:
            logger.warning(f"Error stopping AlertService: {e}")

        try:
            self.heatmap.stop()
        except Exception as e:
            logger.warning(f"Error stopping HeatmapService: {e}")

        self.started = False
        state.update_health_status(camera_connected=False, db_status="OFFLINE", ai_status="OFFLINE")
        logger.info("✅ All services stopped successfully.")


# -------------------------------------------------
# Global Shared Container Instance
# -------------------------------------------------

container = ServiceContainer()
