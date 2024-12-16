import requests
import os

def fetch_weather_data():
    # Replace with your API endpoint and key
    api_key = os.environ.get('WEATHER_API_KEY')
    location = "Bengaluru"
    response = requests.get(f"https://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}")
    data = response.json()
    temperature = data['main']['temp'] - 273.15  # Convert from Kelvin to Celsius
    will_rain = 'rain' in data
    return {'temperature': temperature, 'will_rain': will_rain}
