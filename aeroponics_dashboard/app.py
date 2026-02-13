from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from flask_login import LoginManager, login_user, login_required, logout_user, UserMixin, current_user
from flask_bcrypt import Bcrypt
from database import get_conn, DB_PATH
from sensors import get_live_data
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
app.secret_key = "replace-with-a-strong-secret-key"

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"


class User(UserMixin):
    def __init__(self, id, username, password_hash):
        self.id = id
        self.username = username
        self.password_hash = password_hash

    @staticmethod
    def get_by_username(username):
        with get_conn() as conn:
            c = conn.cursor()
            c.execute("SELECT id, username, password_hash FROM users WHERE username=?", (username,))
            row = c.fetchone()
            return User(*row) if row else None

    @staticmethod
    def get_by_id(user_id):
        with get_conn() as conn:
            c = conn.cursor()
            c.execute("SELECT id, username, password_hash FROM users WHERE id=?", (user_id,))
            row = c.fetchone()
            return User(*row) if row else None


@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(int(user_id))


# --- Logging helper ---
def log_reading(data):
    with get_conn() as conn:
        c = conn.cursor()
        c.execute("""
            INSERT INTO readings (timestamp, temperature, humidity, ph, co_ppm)
            VALUES (?, ?, ?, ?, ?)
        """, (
            datetime.utcnow().isoformat(),
            data["temperature"],
            data["humidity"],
            data["ph"],
            data["co_ppm"]
        ))
        conn.commit()


# --- Scheduler for hourly logging ---
def log_job():
    data = get_live_data()
    log_reading(data)


scheduler = BackgroundScheduler()
scheduler.add_job(log_job, 'interval', hours=1)
scheduler.start()


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = User.get_by_username(username)
        if not user or not bcrypt.check_password_hash(user.password_hash, password):
            flash("Invalid username or password", "error")
            return redirect(url_for("login"))
        login_user(user, remember=True)
        return redirect(url_for("dashboard"))
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/")
@login_required
def dashboard():
    return render_template("dashboard.html")


@app.route("/api/data")
@login_required
def api_data():
    data = get_live_data()
    colors = data.get("colors", {})
    total = sum(colors.values()) or 1
    normalized = {k: round(v * 100 / total, 2) for k, v in colors.items()}
    data["colors"] = normalized
    return jsonify(data)


@app.route("/api/history")
@login_required
def api_history():
    with get_conn() as conn:
        c = conn.cursor()
        c.execute("SELECT timestamp, temperature, humidity, ph, co_ppm FROM readings ORDER BY timestamp DESC LIMIT 24")
        rows = c.fetchall()
    history = [
        {"timestamp": r[0], "temperature": r[1], "humidity": r[2], "ph": r[3], "co_ppm": r[4]}
        for r in rows
    ]
    return jsonify(history)


@app.route("/api/range", methods=["POST"])
@login_required
def api_range():
    start = request.json.get("start")
    end = request.json.get("end")
    with get_conn() as conn:
        c = conn.cursor()
        c.execute("""
            SELECT timestamp, temperature, humidity, ph, co_ppm
            FROM readings
            WHERE timestamp BETWEEN ? AND ?
            ORDER BY timestamp ASC
        """, (start, end))
        rows = c.fetchall()
    history = [
        {"timestamp": r[0], "temperature": r[1], "humidity": r[2], "ph": r[3], "co_ppm": r[4]}
        for r in rows
    ]
    return jsonify(history)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
