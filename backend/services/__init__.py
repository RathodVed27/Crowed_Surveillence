"""
services package
-------------------------------------------------------
Backward compatibility shim exporting singleton services
from the enterprise ServiceContainer in core.shared_services.
Uses Python 3.7+ __getattr__ lazy loading to avoid circular imports.
-------------------------------------------------------
"""


def __getattr__(name):
    if name in ("camera", "tracker", "sensor", "analytics", "alerts", "heatmap"):
        from core.shared_services import container
        return getattr(container, name)
    raise AttributeError(f"module 'services' has no attribute '{name}'")
