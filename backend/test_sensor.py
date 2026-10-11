from sensor_reader import SensorReader

sensor = SensorReader()

while True:

    data = sensor.read()

    print(data)