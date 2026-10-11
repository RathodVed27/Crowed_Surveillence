from services.analytics_service import AnalyticsService

service = AnalyticsService()

tracking = {

    "count": 18,

    "occupancy": 18,

    "unique": 18,

    "entry": 0,

    "exit": 0,

    "people": [],

    "frame": None

}

sensor = {

    "piezo": 230,

    "ir": 1,

    "sw420": 1

}

result = service.process(

    tracking,

    sensor

)

print(result)

print()

print(service.dashboard_data())

service.stop()