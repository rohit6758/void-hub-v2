from app import app, db, User
from werkzeug.security import generate_password_hash

with app.app_context():
    u = User.query.filter_by(username="Rohit").first() # Change "Rohit" to any user
    if u:
        u.password = generate_password_hash("123", method='pbkdf2:sha256')
        db.session.commit()
        print(f"✅ Password for {u.username} reset to: 123")
    else:
        print("❌ User not found.")