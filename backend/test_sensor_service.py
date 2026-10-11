from services.sensor_service import SensorService

sensor = SensorService()

sensor.start()

try:

    while True:

        data = sensor.read()

        print(data)

except KeyboardInterrupt:

    sensor.stop()