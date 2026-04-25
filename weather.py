import requests

API_KEY = "af1e04d1b97ba06f14aaa5d742cf3f82"

def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    
    response = requests.get(url)
    data = response.json()

    temp = data['main']['temp']
    humidity = data['main']['humidity']

    return temp, humidity