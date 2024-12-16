from twilio.rest import Client
import os
from app.weather import fetch_weather_data


def send_alerts():
    with app.app_context():
        from app import db
        from app.models import User

        users = User.query.filter_by(is_active=True, sms_enabled=True).all()
    for user in users:
        phone_number = user.phone_number
        if not phone_number.startswith('+'):
            phone_number = '+91' + phone_number

        weather_data = fetch_weather_data()  # Fetch weather data
        if weather_data['will_rain']:
            message = f"Good morning {user.username}! It will rain today with a temperature of {weather_data['temperature']}°C."
        else:
            message = f"Good morning {user.username}! No rain expected today with a temperature of {weather_data['temperature']}°C."

        client = Client(os.environ['TWILIO_ACCOUNT_SID'], os.environ['TWILIO_AUTH_TOKEN'])
        client.messages.create(body=message, from_=os.environ['TWILIO_PHONE_NUMBER'], to=user.phone_number)
