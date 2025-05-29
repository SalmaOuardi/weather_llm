from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from pydantic import BaseModel
from typing import List

from app.db import (get_user_favorites, add_favorites,
                    remove_favorite)
from app.auth import (authenticate_user, create_access_token,
                      get_current_user, user_exists, create_user)
from app.scraper import (get_city_place_id, fetch_html_page,
                         parse_weather_from_html)
from app.utils import (normalize_city, get_cached_weather,
                       set_cached_weather)


app = FastAPI()

# ===== AUTH ENDPOINTS =====

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="who even are you?")
    access_token = create_access_token(
        data={"sub": user},
        expires_delta=timedelta(minutes=60)
    )
    return {"access_token": access_token, "token_type": "bearer"}

#optional endpoint to show who's logged in (can remove)
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
def add_favorites_endpoint(fav: FavoritesIn, current_user: str = Depends(get_current_user)):
    add_favorites(current_user, fav.cities)
    return {"msg": "favorites updated", "favorites": get_user_favorites(current_user)}

@app.delete("/favorites")
def remove_favorite_endpoint(data: RemoveFavoriteIn, current_user: str = Depends(get_current_user)):
    remove_favorite(current_user, data.city)
    return {"msg": f"{data.city} removed from favorites", "favorites": get_user_favorites(current_user)}


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
      set_cached_weather(matched_city, weather["temperature"], weather["weather_condition"])
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
