from sensor_reader import SensorReader
import time


sensor = SensorReader(
    port="COM3",
    baud_rate=115200
)

sensor.start()

print("Waiting for sensor...")
print("Press CTRL+C to stop.\n")

try:

    while True:

        data = sensor.get_data()

        print(
            "Sensor Data:",
            data
        )

        time.sleep(1)

except KeyboardInterrupt:

    sensor.stop()