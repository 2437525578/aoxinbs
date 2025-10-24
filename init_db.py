# init_db.py
from app import create_app
from models import db, User, Chemical
from werkzeug.security import generate_password_hash
from datetime import date, timedelta

app = create_app()

with app.app_context():
    db.drop_all()
    db.create_all()

    # Create a default admin user
    hashed_password = generate_password_hash("admin123")
    admin_user = User(username="admin", email="admin@example.com", password_hash=hashed_password, role="admin")
    db.session.add(admin_user)
    db.session.commit()

    print("Database initialized and default admin user created.")
