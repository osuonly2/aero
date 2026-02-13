
from database import init_db
from set_password import ensure_user

if __name__ == "__main__":
    init_db()
    ensure_user("admin", "admin123")
    print("Database initialized. Default login: admin / admin123")
