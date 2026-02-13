
import argparse
from flask_bcrypt import Bcrypt
from database import get_conn

bcrypt = Bcrypt()

def ensure_user(username: str, password: str):
    pw_hash = bcrypt.generate_password_hash(password).decode("utf-8")
    with get_conn() as conn:
        c = conn.cursor()
        # Try update; if no row, insert
        c.execute("UPDATE users SET password_hash=? WHERE username=?", (pw_hash, username))
        if c.rowcount == 0:
            c.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, pw_hash))
        conn.commit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--username", required=True)
    parser.add_argument("--password", required=True)
    args = parser.parse_args()
    ensure_user(args.username, args.password)
    print(f"Password set for user {args.username}.")
