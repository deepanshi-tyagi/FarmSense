import os

import requests
from dotenv import load_dotenv

load_dotenv(override=True)


def get_weather(city):
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OPENWEATHER_API_KEY is not configured. Add it to your .env file."
        )

    response = requests.get(
        "https://api.openweathermap.org/data/2.5/weather",
        params={"q": city.strip(), "appid": api_key, "units": "metric"},
        timeout=10,
    )

    try:
        data = response.json()
    except requests.exceptions.JSONDecodeError as exc:
        raise RuntimeError("Weather service returned an invalid response.") from exc

    if response.status_code != 200:
        raise RuntimeError(data.get("message", "Weather service request failed."))

    return {
        "city": city.strip(),
        "temperature": data["main"]["temp"],
        "humidity": data["main"]["humidity"],
        "condition": data["weather"][0]["description"],
        "wind_speed": data["wind"]["speed"],
    }
