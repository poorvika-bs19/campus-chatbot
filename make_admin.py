from app import app, db, User

email = input("Enter the email to make admin: ").strip()

with app.app_context():
    user = User.query.filter_by(email=email).first()
    if not user:
        print("No user found with that email. Sign up first, then run this script.")
    else:
        user.is_admin = True
        db.session.commit()
        print(f"{email} is now an admin!")