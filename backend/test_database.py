from database import CrowdDatabase

db = CrowdDatabase()

db.save_crowd_data(

    people=15,

    piezo=220,

    ir=1,

    sw420=1,

    risk_score=88,

    crowd_status="HIGH",

    trend="Increasing"

)

db.save_alert(

    "HIGH",

    "High Crowd Detected"

)

print(db.latest_data())

print()

print(db.alerts())

db.close()