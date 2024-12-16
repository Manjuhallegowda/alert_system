from app import create_app, db
from app.models import User

app = create_app()

with app.app_context():
    # Create an admin user
    admin = User(username='admin', email='admin@example.com', phone_number='1234567890')
    admin.set_password('admin123')  # Set a strong password
    admin.is_admin = True  # Set the user as an admin
    admin.is_active = True # Set the user as an is active
    db.session.add(admin)
    db.session.commit()

print('Admin user created successfully!')
