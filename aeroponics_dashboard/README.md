
# Smart Aeroponics Flask Dashboard (Starter)

This is a ready-to-run starter for your aeroponics dashboard.

## Features
- Login (Flask-Login + bcrypt; default user `admin` / password `admin123`)
- Dashboard page with a pie chart for Huskylens color percentages
- REST endpoint `/api/data` that returns live readings (currently mocked in `sensors.py`)
- SQLite database for users (you can extend it for sensor history)

## Quick Start (PC or Raspberry Pi)
```bash
# 1) Create and activate a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 2) Install dependencies
pip install -r requirements.txt

# 3) Initialize the database and default admin user
python init_db.py

# 4) Run the app
python app.py
# Open http://127.0.0.1:5000  (PC)
# Or http://<raspberry-pi-ip>:5000  (from phone/laptop on same network)
```

## Change Admin Password
After first login, change the password by running:
```bash
python set_password.py --username admin --password NEW_PASSWORD
```

## Hook Up Real Sensors
- Edit `sensors.py` — replace `get_live_data()` with code that reads:
  - Huskylens (I2C) and computes color percentages
  - DHT22 / pH / MQ-7 (via Arduino or direct)
- The frontend pie chart and cards will automatically update using `/api/data`.

## Autostart on Raspberry Pi (optional)
Create a systemd service to auto-start on boot:
```ini
# /etc/systemd/system/aeroponics.service
[Unit]
Description=Aeroponics Flask Dashboard
After=network.target

[Service]
User=pi
WorkingDirectory=/home/pi/aeroponics_flask
Environment="PATH=/home/pi/aeroponics_flask/.venv/bin"
ExecStart=/home/pi/aeroponics_flask/.venv/bin/python app.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```
Enable:
```bash
sudo systemctl daemon-reload
sudo systemctl enable aeroponics.service
sudo systemctl start aeroponics.service
```
