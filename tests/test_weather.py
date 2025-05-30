def test_weather_search(client):
    # Sign up & login first
    client.post("/signup", json={"username": "jim", "password": "pam4ever"})
    login = client.post(
        "/login", data={"username": "jim", "password": "pam4ever"}
    )
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Test weather endpoint
    r = client.get("/weather", params={"city": "Paris"}, headers=headers)
    assert r.status_code == 200
    assert "city" in r.json()
    assert "temperature" in r.json()
    assert "weather_condition" in r.json()
