import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.set_page_config(page_title="Guided Weather ☀️", page_icon="🌤️")

if "token" not in st.session_state:
    st.session_state.token = None

st.title("guided weather 🌤️")

if st.session_state.token is None:
    # Only show login/signup if not logged in
    tab_login, tab_signup = st.tabs(["login", "sign up"])

    with tab_login:
        user = st.text_input("username", key="user")
        pwd = st.text_input("password", type="password", key="pwd")
        if st.button("login"):
            resp = requests.post(f"{API_URL}/login", data={"username": user, "password": pwd})
            if resp.ok:
                st.session_state.token = resp.json()["access_token"]
                st.success("you're in, fam ✨")
                st.rerun()
            else:
                st.error(resp.json().get("detail", "login failed"))

    with tab_signup:
        new_user = st.text_input("new username", key="new_user")
        new_pwd = st.text_input("new password", type="password", key="new_pwd")
        if st.button("sign up"):
            resp = requests.post(f"{API_URL}/signup", json={"username": new_user, "password": new_pwd})
            if resp.ok:
                st.success("user created! you can now log in.")
            else:
                st.error(resp.json().get("detail", "couldn't create user"))

else:
    # Only show weather and favorites if logged in!
    headers = {"Authorization": f"Bearer {st.session_state.token}"}

    st.header("search any city's weather")
    city_query = st.text_input("city name", key="search")
    if st.button("get weather"):
        r = requests.get(f"{API_URL}/weather", params={"city": city_query}, headers=headers)
        if r.ok:
            data = r.json()
            st.write(f"**Weather in {data.get('city','?')}:** {data.get('temperature','?')}°C, {data.get('weather_condition','?')}")
        else:
            st.error(r.json().get("error", "something went wrong"))

    st.header("your favorites dashboard")
    favs = []
    fav_resp = requests.get(f"{API_URL}/favorites", headers=headers)
    if fav_resp.ok:
        favs = fav_resp.json()
        for fav in favs:
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"🌟 {fav['city']}: {fav['temperature']}°C, {fav['weather_condition']}")
            with col2:
                if st.button(f"remove {fav['city']}", key=f"rem_{fav['city']}"):
                    rem = requests.delete(f"{API_URL}/favorites", headers=headers, json={"city": fav["city"]})
                    st.rerun()

    st.subheader("add city to favorites")
    add_city = st.text_input("city to add", key="addfav")
    if st.button("add to favorites"):
        r = requests.post(f"{API_URL}/favorites", headers=headers, json={"cities": [add_city]})
        if r.ok:
            st.success("city added to favorites!")
            st.rerun()
        else:
            st.error("could not add city")

    # LOGOUT
    if st.button("logout"):
        st.session_state.token = None
        st.rerun()
