import requests
from bs4 import BeautifulSoup
from app.utils import parse_city_country


def get_city_place_id(user_input):
    """
    Given a user input string, parse out city and country, query weather.com's internal API,
    and return (place_id, matched_city_name) for the closest match.
    """
    city, country_code = parse_city_country(user_input)
    api_url = "https://weather.com/api/v1/p/redux-dal"
    payload = [
        {
            "name": "getSunV3LocationSearchUrlConfig",
            "params": {
                "language": "en-US",
                "locationType": "locale",
                "query": city,
            },
        }
    ]
    headers = {
        "Content-Type": "application/json",
        "Origin": "https://weather.com",
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
        ),
        "Referer": "https://weather.com",
    }

    try:
        resp = requests.post(api_url, json=payload, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        config = data["dal"]["getSunV3LocationSearchUrlConfig"]
        first_key = next(iter(config))
        locations = config[first_key]["data"]["location"]
        user_city = city.strip().lower()

        # 1. Try exact city name + country code match
        if country_code:
            for city_name, cc, place_id in zip(
                locations["city"],
                locations["countryCode"],
                locations["placeId"],
            ):
                if (
                    city_name
                    and cc == country_code
                    and city_name.strip().lower() == user_city
                ):
                    return place_id, city_name

            # 2. Fallback: first city in correct country
            for city_name, cc, place_id in zip(
                locations["city"],
                locations["countryCode"],
                locations["placeId"],
            ):
                if cc == country_code and city_name:
                    return place_id, city_name

        # 3. No country code: fallback to first city match in API response
        for city_name, place_id in zip(locations["city"], locations["placeId"]):
            if city_name and city_name.strip().lower() == user_city:
                return place_id, city_name

        # 4. Absolute fallback: first city/place_id in response
        if locations["placeId"]:
            return locations["placeId"][0], locations["city"][0]

        print(f"No matching city found for '{city}' with country '{country_code}'.")
        return None, None

    except requests.RequestException as e:
        print(f"Network or request error: {e}")
        return None, None


def fetch_html_page(place_id):
    """
    Fetches the weather.com page HTML for a given place_id.
    """
    endpoint = f"https://weather.com/weather/today/l/{place_id}"
    headers = {
        "Origin": "https://weather.com",
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
        ),
        "Referer": "https://weather.com",
    }
    try:
        resp = requests.get(endpoint, headers=headers, timeout=10)
        resp.raise_for_status()
        return resp.text
    except requests.RequestException as e:
        print(f"Failed to fetch weather page for {place_id}: {e}")
        return None


def parse_weather_from_html(html_text, city):
    """
    Given HTML text of a city's weather.com page, extract temperature (Celsius) and weather condition.
    """
    soup = BeautifulSoup(html_text, "html.parser")

    # get temperature (default on site is F°, so convert to C°)
    temp_span = soup.find("span", {"data-testid": "TemperatureValue"})
    if temp_span:
        temp_text = temp_span.get_text(strip=True)
        temp_digits = "".join(filter(str.isdigit, temp_text))
        temperature = round((int(temp_digits) - 32) * 5 / 9) if temp_digits else None
    else:
        temperature = None

    # get weather condition
    condition_div = soup.find("div", {"data-testid": "wxPhrase"})
    weather_condition = (
        condition_div.get_text(strip=True).lower() if condition_div else None
    )

    return {
        "city": city,
        "temperature": temperature,
        "weather_condition": weather_condition,
    }


if __name__ == "__main__":
    user_input = "glasgow"
    place_id, matched_city = get_city_place_id(user_input)
    if place_id and matched_city:
        html = fetch_html_page(place_id)
        if html:
            weather = parse_weather_from_html(html, matched_city)
            print(weather)
        else:
            print("Failed to fetch city weather page.")
    else:
        print("Could not find a matching city.")
