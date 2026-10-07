import time
from datetime import datetime

import psutil
import requests
from rich.console import Group
from rich.live import Live
from rich.panel import Panel
from rich.table import Table

# opsec level: New York metropolitan area
LATITUDE = 40.71
LONGITUDE = -74.01
WEATHER_REFRESH_SECONDS = 600

# all the codes to refer to diff weather types
WEATHER_CODES = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 51: "Light drizzle", 61: "Light rain", 63: "Rain",
    65: "Heavy rain", 71: "Light snow", 73: "Snow", 75: "Heavy snow",
    80: "Rain showers", 95: "Thunderstorm",
}

# func which gets the weather from open-meteo
def fetch_weather():
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "current": "temperature_2m,apparent_temperature,relative_humidity_2m,wind_speed_10m,weather_code",
        "temperature_unit": "fahrenheit",
        "wind_speed_unit": "mph",
    }
    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        current = data.get("current") or {}
        return {
            "temp": float(current["temperature_2m"]),
            "feels_like": float(current["apparent_temperature"]),
            "humidity": current["relative_humidity_2m"],
            "wind": float(current["wind_speed_10m"]),
            "description": WEATHER_CODES.get(current["weather_code"], "Unknown"),
        }
    except (requests.RequestException, KeyError, TypeError, ValueError):
        return None

def make_bar(percent, width=20):
    filled = int(width * percent / 100)
    return "█" * filled + "░" * (width - filled)

def build_dashboard(weather):
    now = datetime.now()
    clock = Panel(
        f"[bold cyan]{now.strftime('%H:%M:%S')}[/]\n{now.strftime('%A, %B %d, %Y')}",
        title="Time",
    )

    if weather:
        weather_text = (
            f"[bold]{weather['temp']:.0f}°F[/] {weather['description']}\n"
            f"Feels like {weather['feels_like']:.0f}°F\n"
            f"Humidity {weather['humidity']}%  Wind {weather['wind']:.0f} mph"
        )
    else:
        weather_text = "[red]Weather unavailable[/]"
    weather_panel = Panel(weather_text, title="Weather")

    cpu = psutil.cpu_percent(interval=None)
    memory = psutil.virtual_memory().percent
    disk = psutil.disk_usage("/").percent
    table = Table.grid(padding=(0, 2))
    table.add_row("CPU", make_bar(cpu), f"{cpu:5.1f}%")
    table.add_row("Memory", make_bar(memory), f"{memory:5.1f}%")
    table.add_row("Disk", make_bar(disk), f"{disk:5.1f}%")
    resources = Panel(table, title="Resources")

    return Group(clock, weather_panel, resources)

# main time
def main():
    weather = fetch_weather()
    last_fetch = time.monotonic()
    psutil.cpu_percent(interval=None)

    with Live(build_dashboard(weather), refresh_per_second=4, screen=True) as live:
        try:
            while True:
                if time.monotonic() - last_fetch > WEATHER_REFRESH_SECONDS:
                    weather = fetch_weather() or weather
                    last_fetch = time.monotonic()

                live.update(build_dashboard(weather))
                time.sleep(1)
        except KeyboardInterrupt:
            pass

if __name__ == "__main__":
    main()
                
    