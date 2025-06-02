from fastapi import FastAPI, Depends, HTTPException, Body
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse
from datetime import timedelta
from pydantic import BaseModel
from typing import List
import json

from app.db import get_user_favorites, add_favorites, remove_favorite
from app.auth import (
    authenticate_user,
    create_access_token,
    get_current_user,
    user_exists,
    create_user,
)
from app.scraper import (
    get_city_place_id,
    fetch_html_page,
    parse_weather_from_html,
)
from app.utils import normalize_city, get_cached_weather, set_cached_weather
from app.llm import ollama_generate


app = FastAPI()


@app.get("/", response_class=HTMLResponse)
def root():
    return """
    <html>
        <head>
            <title>Guided Weather</title>
        </head>
        <body>
            <h1>Welcome to Guided Weather API!</h1>
            <p>Visit <a href="/docs">/docs</a> for the interactive API documentation.</p>
        </body>
    </html>
    """


# ===== AUTH ENDPOINTS =====


@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="who even are you?")
    access_token = create_access_token(
        data={"sub": user}, expires_delta=timedelta(minutes=60)
    )
    return {"access_token": access_token, "token_type": "bearer"}


# optional endpoint to show who's logged in (can remove)
@app.get("/whoami")
def whoami(current_user: str = Depends(get_current_user)):
    return {"user": current_user}


# ===== USER FAVORITES LOGIC =====


class FavoritesIn(BaseModel):
    cities: List[str]


class RemoveFavoriteIn(BaseModel):
    city: str


@app.get("/favorites")
def get_favorites(current_user: str = Depends(get_current_user)):
    favs = get_user_favorites(current_user)
    result = []
    for city in favs:
        place_id, matched_city = get_city_place_id(city)
        if place_id:
            html = fetch_html_page(place_id)
            if html:
                result.append(parse_weather_from_html(html, matched_city))
    return result


@app.post("/favorites")
def add_favorites_endpoint(
    fav: FavoritesIn, current_user: str = Depends(get_current_user)
):
    add_favorites(current_user, fav.cities)
    return {
        "msg": "favorites updated",
        "favorites": get_user_favorites(current_user),
    }


@app.delete("/favorites")
def remove_favorite_endpoint(
    data: RemoveFavoriteIn, current_user: str = Depends(get_current_user)
):
    remove_favorite(current_user, data.city)
    return {
        "msg": f"{data.city} removed from favorites",
        "favorites": get_user_favorites(current_user),
    }


# ===== WEATHER SEARCH ENDPOINT =====


@app.get("/weather")
def get_weather(city: str, current_user: str = Depends(get_current_user)):
    city = normalize_city(city)
    print("USER INPUT:", city)
    # 1. Try cache
    cached = get_cached_weather(city)
    if cached:
        print("[CACHE HIT]", cached)
        return cached
    # 2. If not, scrape and cache
    place_id, matched_city = get_city_place_id(city)
    matched_city = normalize_city(matched_city)
    print("MATCHED_CITY:", matched_city)
    if not place_id:
        return {"error": "this city isn't on the map, michael"}
    html = fetch_html_page(place_id)
    if not html:
        return {"error": "weather.com is on strike today"}
    weather = parse_weather_from_html(html, matched_city)
    set_cached_weather(
        matched_city, weather["temperature"], weather["weather_condition"]
    )
    return weather


# ===== BONUS: SIGNUP =====


class SignupIn(BaseModel):
    username: str
    password: str


@app.post("/signup")
def signup(data: SignupIn):
    if user_exists(data.username):
        raise HTTPException(status_code=400, detail="user already exists!")
    create_user(data.username, data.password)
    return {"msg": "you can now login!"}


# ===== LLM =====


@app.get("/summary")
def get_weather_summary(current_user: str = Depends(get_current_user)):
    favs = get_user_favorites(current_user)
    if not favs:
        return {"summary": "no favorite cities found!"}
    weather_data = []
    for city in favs:
        place_id, matched_city = get_city_place_id(city)
        if place_id:
            cached = get_cached_weather(matched_city)
            if not cached:
                html = fetch_html_page(place_id)
                weather = parse_weather_from_html(html, matched_city)
                set_cached_weather(
                    matched_city,
                    weather["temperature"],
                    weather["weather_condition"],
                )
                weather_data.append(weather)
            else:
                weather_data.append(cached)
    weather_str = "\n".join(
        f"{w['city']}: {w['temperature']}°C, {w['weather_condition']}"
        for w in weather_data
    )
    prompt = f"""
You are a weather assistant.

Summarize the current weather for these cities in 1-2 natural language sentences, using only the provided data:

{weather_str}

Be concise, clear, and mention all cities with noteworthy conditions. 
"""
    summary = ollama_generate(prompt)
    return {"summary": summary}


@app.post("/ask")
def ask_weather_question(
    q: dict = Body(...), current_user: str = Depends(get_current_user)
):
    favs = get_user_favorites(current_user)
    if not favs:
        return {
            "answer": "no favorite cities to search.",
            "matchingCities": [],
        }
    weather_data = []
    for city in favs:
        place_id, matched_city = get_city_place_id(city)
        if place_id:
            cached = get_cached_weather(matched_city)
            if not cached:
                html = fetch_html_page(place_id)
                weather = parse_weather_from_html(html, matched_city)
                set_cached_weather(
                    matched_city,
                    weather["temperature"],
                    weather["weather_condition"],
                )
                weather_data.append(weather)
            else:
                weather_data.append(cached)
    weather_str = "\n".join(
        f"{w['city']}: {w['temperature']}°C, {w['weather_condition']}"
        for w in weather_data
    )
    prompt = f"""
You are a helpful weather assistant.

You will be given a list of cities with their current weather data. 
Answer the user's natural language question using ONLY this data.

Be concise and specific. If you don't know, say so. 
At the end, always return a JSON object with:
- "answer": a natural language answer to the question
- "matchingCities": a list of city names (from the data) that match the user's query, or an empty list if none fit

**Format your entire response as a valid JSON object using double quotes, like this:**
{{"answer": "...", "matchingCities": ["City1", "City2"]}}

Weather data:
{weather_str}

Question:
{q['question']}

Remember: ONLY use the weather data provided above. Do NOT mention cities that are not in the list. 
"""
    raw_response = ollama_generate(prompt)
    # try parsing the output as JSON
    try:
        # Sometimes the model may output text before the JSON; try to extract the JSON part
        json_start = raw_response.find("{")
        if json_start != -1:
            resp_json = raw_response[json_start:]
            return json.loads(resp_json)
        else:
            return {"answer": raw_response, "matchingCities": []}
    except Exception as e:
        return {
            "answer": raw_response,
            "matchingCities": [],
            "error": f"JSON decode failed: {e}",
        }
