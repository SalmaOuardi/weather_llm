def test_signup_and_login(client):
    # signup
    resp = client.post("/signup", json={"username": "pam", "password": "beesly"})
    assert resp.status_code == 200

    # duplicate signup
    resp2 = client.post("/signup", json={"username": "pam", "password": "beesly"})
    assert resp2.status_code == 400

    # login
    resp3 = client.post("/login", data={"username": "pam", "password": "beesly"})
    assert resp3.status_code == 200
    assert "access_token" in resp3.json()
