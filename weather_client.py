"""
weather_client.py — 100% free ground weather + location lookup for the Live
Match Center.

Uses Open-Meteo (https://open-meteo.com) for both geocoding (venue name ->
lat/lon) and current weather. Open-Meteo's public endpoints need NO API key,
NO signup and NO credit card — perfect for a small academy app. Results are
cached for 30 minutes per venue so we don't hammer the API on every rerun.
"""

import requests
import streamlit as st

GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"

# WMO weather codes -> (emoji, short label)
_WMO = {
    0: ("☀️", "Clear Sky"), 1: ("🌤️", "Mainly Clear"), 2: ("⛅", "Partly Cloudy"),
    3: ("☁️", "Overcast"), 45: ("🌫️", "Fog"), 48: ("🌫️", "Fog"),
    51: ("🌦️", "Light Drizzle"), 53: ("🌦️", "Drizzle"), 55: ("🌧️", "Heavy Drizzle"),
    61: ("🌦️", "Light Rain"), 63: ("🌧️", "Rain"), 65: ("🌧️", "Heavy Rain"),
    71: ("🌨️", "Light Snow"), 73: ("🌨️", "Snow"), 75: ("❄️", "Heavy Snow"),
    80: ("🌦️", "Rain Showers"), 81: ("🌧️", "Rain Showers"), 82: ("⛈️", "Violent Showers"),
    95: ("⛈️", "Thunderstorm"), 96: ("⛈️", "Thunderstorm + Hail"), 99: ("⛈️", "Thunderstorm + Hail"),
}


def _wmo_lookup(code):
    return _WMO.get(code, ("🌡️", "—"))


@st.cache_data(ttl=1800, show_spinner=False)
def geocode_venue(venue_text: str):
    """venue_text -> {'lat', 'lon', 'display_name'} or None."""
    if not venue_text or not venue_text.strip():
        return None
    try:
        r = requests.get(GEOCODE_URL, params={"name": venue_text.strip(), "count": 1}, timeout=6)
        r.raise_for_status()
        data = r.json()
        results = data.get("results")
        if not results:
            return None
        top = results[0]
        parts = [top.get("name"), top.get("admin1"), top.get("country")]
        display_name = ", ".join(p for p in parts if p)
        return {"lat": top["latitude"], "lon": top["longitude"], "display_name": display_name}
    except Exception:
        return None


@st.cache_data(ttl=1800, show_spinner=False)
def get_current_weather(lat: float, lon: float):
    """lat/lon -> {'temp_c', 'wind_kph', 'humidity', 'emoji', 'label'} or None."""
    try:
        r = requests.get(WEATHER_URL, params={
            "latitude": lat, "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m",
        }, timeout=6)
        r.raise_for_status()
        cur = r.json().get("current", {})
        emoji, label = _wmo_lookup(cur.get("weather_code"))
        return {
            "temp_c": cur.get("temperature_2m"),
            "humidity": cur.get("relative_humidity_2m"),
            "wind_kph": cur.get("wind_speed_10m"),
            "emoji": emoji,
            "label": label,
        }
    except Exception:
        return None


def get_weather_for_venue(venue_text: str):
    """Convenience: venue name -> combined location + weather dict, or None
    if the venue can't be geocoded / weather API is unreachable (e.g. no
    internet on this machine) — callers should handle None gracefully."""
    loc = geocode_venue(venue_text)
    if not loc:
        return None
    wx = get_current_weather(loc["lat"], loc["lon"])
    if not wx:
        return None
    return {**loc, **wx}


def render_weather_strip(venue_text: str):
    """Renders the compact weather + location strip under the scoreboard.
    Silently renders nothing if venue is blank or lookup fails (e.g. offline)
    — never blocks or errors out the live scoring screen."""
    if not venue_text:
        return
    info = get_weather_for_venue(venue_text)
    if not info:
        return
    temp = info.get("temp_c")
    temp_str = f"{round(temp)}°C" if temp is not None else "—"
    st.markdown(
        f'''<div class="wx-strip">
            <div class="wx-item"><span class="wx-emoji">📍</span> {info["display_name"]}</div>
            <div class="wx-item"><span class="wx-emoji">{info["emoji"]}</span> {info["label"]}, {temp_str}</div>
            <div class="wx-item"><span class="wx-emoji">💧</span> {info.get("humidity", "—")}%</div>
            <div class="wx-item"><span class="wx-emoji">🌬️</span> {info.get("wind_kph", "—")} km/h</div>
        </div>''',
        unsafe_allow_html=True,
    )
