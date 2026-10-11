from services.alert_service import AlertService

alert = AlertService()

analytics = {

    "status": "HIGH",

    "alert": "Security Attention Required"

}

alert.process(analytics)

print(alert.get_alerts())

alert.stop()