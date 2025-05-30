import json


def test_favorites_flow(client):
    # Signup & login
    client.post("/signup", json={"username": "kevin", "password": "notweird"})
    login = client.post(
        "/login", data={"username": "kevin", "password": "notweird"}
    )
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Add to favorites
    resp = client.post(
        "/favorites", headers=headers, json={"cities": ["Paris"]}
    )
    assert resp.status_code == 200
    assert any(city.lower() == "paris" for city in resp.json()["favorites"])

    # Get favorites
    resp2 = client.get("/favorites", headers=headers)
    assert resp2.status_code == 200
    assert any(fav.get("city", "").lower() == "paris" for fav in resp2.json())

    # Remove favorite (now correct)
    resp3 = client.request(
        "DELETE",
        "/favorites",
        headers={**headers, "Content-Type": "application/json"},
        data=json.dumps({"city": "Paris"}),
    )
    assert resp3.status_code == 200
    assert all(city.lower() != "paris" for city in resp3.json()["favorites"])
