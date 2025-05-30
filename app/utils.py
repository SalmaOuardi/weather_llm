import re
import datetime
from app.country_map import COUNTRY_NAME_TO_CODE
from app.db import SessionLocal, WeatherCache


def normalize_city(city):
    return city.strip().lower()


# ===== PARSE CITY/COUNTRY =====


def parse_city_country(user_input):

    s = user_input.strip()

    # split on common delimiters
    parts = re.split(r"[,/\-\|]", s)
    if len(parts) > 1:
        city = parts[0].strip()
        country = parts[1].strip().lower()
        country_code = COUNTRY_NAME_TO_CODE.get(country)
        return city, country_code

    # try matching from end for space seperated country names
    words = s.split()
    for i in range(1, len(words)):
        country_candidate = " ".join(words[i:]).strip().lower()
        country_code = COUNTRY_NAME_TO_CODE.get(country_candidate)
        if country_code:
            city = " ".join(words[:i]).strip()
            return city, country_code

    # just city, no country
    return s, None


# ===== WEATHER CACHING LOGIC =====

CACHE_MINUTES = 15


def get_cached_weather(city):
    now = datetime.datetime.now()
    with SessionLocal() as db:
        record = (
            db.query(WeatherCache).filter(WeatherCache.city == city).first()
        )
        if (
            record
            and (now - record.fetched_at).total_seconds() < CACHE_MINUTES * 60
        ):
            return {
                "city": city,
                "temperature": record.temperature,
                "weather_condition": record.condition,
            }
        return None


def set_cached_weather(city, temperature, condition):
    now = datetime.datetime.now()
    with SessionLocal() as db:
        cache = (
            db.query(WeatherCache).filter(WeatherCache.city == city).first()
        )
        if cache:
            cache.temperature = temperature
            cache.condition = condition
            cache.fetched_at = now
        else:
            cache = WeatherCache(
                city=city,
                temperature=temperature,
                condition=condition,
                fetched_at=now,
            )
            db.add(cache)
        db.commit()
