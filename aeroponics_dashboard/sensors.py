import serial
import time

SERIAL_PORT = "/dev/ttyUSB0"
BAUD_RATE = 9600

ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=2)

def get_live_data():
    data = {
        "colors": {},
        "temperature": None,
        "humidity": None,
        "ph": None,
        "co_ppm": None,
        "pump_on": False,
        "timestamp": int(time.time())
    }

    try:
        line = ser.readline().decode("utf-8").strip()
        if not line:
            return data

        parts = line.split(",")
        for p in parts:
            p = p.strip()
            if p.startswith("Temp:"):
                data["temperature"] = float(p.split(":")[1].split()[0])
            elif p.startswith("Hum:"):
                data["humidity"] = float(p.split(":")[1].split()[0])
            elif p.startswith("pH:"):
                data["ph"] = float(p.split(":")[1])
            elif p.startswith("CO:"):
                data["co_ppm"] = float(p.split(":")[1].split()[0])

        # Pump state
        if "FillingActive:" in line:
            try:
                active_val = line.split("FillingActive:")[1].split()[0]
                data["pump_on"] = active_val == "1"
            except:
                pass

        # HuskyLens parsing
        if "HuskyLens:" in line:
            husky_val = line.split("HuskyLens:")[1].strip()
            if husky_val != "None":
                data["colors"] = {husky_val: 1}
            else:
                data["colors"] = {}

    except Exception as e:
        print("Parse error:", e)

    return data
