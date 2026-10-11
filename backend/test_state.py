from services.sensor_service import SensorService
from models.state import state
import time


sensor = SensorService()
sensor.start()

print()
print("======================================")
print("   SENSOR + CENTRAL STATE TEST")
print("======================================")
print("Press the piezo repeatedly for 10 seconds.")
print()

start_time = time.time()

while time.time() - start_time < 10:

    data = sensor.read()

    if data["piezo"] > 0:

        print("Sensor Data :", data)
        print("State Piezo :", state.to_dict().get("piezo"))
        print("--------------------------------------")

    time.sleep(0.1)

print()
print("======================================")
print("FINAL STATE")
print("======================================")
print(state.to_dict())
