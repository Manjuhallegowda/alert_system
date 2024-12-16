from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, login_required, current_user, logout_user
from app import db
from app.models import User
from app.forms import RegistrationForm, LoginForm, AdminLoginForm
from app.weather import fetch_weather_data
from twilio.rest import Client
import os
from werkzeug.security import generate_password_hash


main = Blueprint('main', __name__)


@main.route('/')
def home():
    return render_template('home.html')


@main.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user = User(username=form.username.data, email=form.email.data, password_hash=hashed_password,
                    phone_number=form.phone_number.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html', form=form)


@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('main.dashboard'))
        flash('Invalid email or password.', 'danger')
    return render_template('login.html', form=form)


@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.home'))


@main.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    form = AdminLoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data) and user.is_admin:
            login_user(user)
            flash('Admin login successful.', 'success')
            return redirect(url_for('main.admin_dashboard'))
        else:
            flash('Invalid username or password, or not an admin.', 'danger')
    return render_template('admin_login.html', form=form)


@main.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('You do not have access to this page.', 'danger')
        return redirect(url_for('main.home'))
    users = User.query.all()
    return render_template('admin_dashboard.html', users=users)


@main.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    if request.method == 'POST':
        if 'enable_sms' in request.form:
            current_user.sms_enabled = True
            db.session.commit()
            flash('SMS alerts enabled. You will receive weather updates.', 'success')

            # Send SMS immediately after enabling
            weather_data = fetch_weather_data()
            if weather_data['will_rain']:
                message = f"Hello {current_user.username}! You have enabled SMS alerts. It will rain today with a temperature of {weather_data['temperature']}°C."
            else:
                message = f"Hello {current_user.username}! You have enabled SMS alerts. No rain expected today with a temperature of {weather_data['temperature']}°C."

            client = Client(os.environ['TWILIO_ACCOUNT_SID'], os.environ['TWILIO_AUTH_TOKEN'])
            client.messages.create(body=message, from_=os.environ['TWILIO_PHONE_NUMBER'], to=current_user.phone_number)

        elif 'disable_sms' in request.form:
            current_user.sms_enabled = False
            db.session.commit()
            flash('SMS alerts disabled.', 'warning')

    return render_template('dashboard.html')


@main.route('/approve_user/<int:user_id>')
@login_required
def approve_user(user_id):
    if not current_user.is_admin:
        flash('You do not have permission to perform this action.', 'danger')
        return redirect(url_for('main.home'))
    user = User.query.get(user_id)
    if user:
        user.is_active = True
        db.session.commit()
        flash('User approved successfully.', 'success')
    return redirect(url_for('main.admin_dashboard'))


@main.route('/send_alerts')
def send_alerts():
    users = User.query.filter_by(is_active=True).all()
    for user in users:
        if user.sms_enabled:  # Assuming you add this field in the User model
            weather_data = fetch_weather_data()  # Fetch weather data
            if weather_data['will_rain']:
                message = f"Good morning {user.username}! It will rain today with a temperature of {weather_data['temperature']}°C."
            else:
                message = f"Good morning {user.username}! No rain expected today with a temperature of {weather_data['temperature']}°C."

            client = Client(os.environ['TWILIO_ACCOUNT_SID'], os.environ['TWILIO_AUTH_TOKEN'])
            client.messages.create(body=message, from_=os.environ['TWILIO_PHONE_NUMBER'], to=user.phone_number)

    return 'Alerts sent!'
