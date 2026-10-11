from repositories.crowd_repository import CrowdRepository
from repositories.alert_repository import AlertRepository

crowd = CrowdRepository()
alert = AlertRepository()

crowd.save(

    people=20,

    piezo=250,

    ir=1,

    sw420=1,

    risk_score=95,

    crowd_status="EMERGENCY",

    trend="Increasing"

)

alert.save(

    "EMERGENCY",

    "Crowd is extremely high"

)

print()

print(crowd.latest())

print()

print(alert.all())

crowd.close()
alert.close()