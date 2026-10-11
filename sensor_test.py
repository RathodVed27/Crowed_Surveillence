import serial
import time

PORT = "COM3"
BAUD_RATE = 115200

print("Connecting to ESP8266...")

ser = serial.Serial(
    PORT,
    BAUD_RATE,
    timeout=1
)

time.sleep(2)

print("ESP8266 connected successfully.")
print("Waiting for sensor events...")
print("Press CTRL+C to stop.\n")

try:
    while True:

        line = ser.readline().decode(
            "utf-8",
            errors="ignore"
        ).strip()

        if line:
            print("ESP8266:", line)

except KeyboardInterrupt:
    print("\nStopping...")

finally:
    ser.close()
    print("Serial connection closed.")