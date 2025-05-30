import streamlit as st
import requests

API_URL = "http://localhost:8000"
st.set_page_config(
    page_title="Guided Weather", page_icon="🌤️", layout="centered"
)


def small_text(s, color="#888"):
    st.markdown(
        f'<span style="font-size:0.95em;color:{color}">{s}</span>',
        unsafe_allow_html=True,
    )


if "token" not in st.session_state:
    st.session_state.token = None

# Minimal header, centered
st.markdown(
    '<div style="text-align:center;"><h2 style="margin-bottom:2px;">Guided Weather</h2><span style="font-size:1.5em;">🌤️</span></div>',
    unsafe_allow_html=True,
)
st.markdown('<hr style="margin:10px 0 15px 0;">', unsafe_allow_html=True)

if st.session_state.token is None:
    tab_login, tab_signup = st.tabs(["log in", "sign up"])

    with tab_login:
        user = st.text_input("username", key="user")
        pwd = st.text_input("password", type="password", key="pwd")
        if st.button("log in", use_container_width=True):
            with st.spinner("authenticating..."):
                resp = requests.post(
                    f"{API_URL}/login",
                    data={"username": user, "password": pwd},
                )
            if resp.ok:
                st.session_state.token = resp.json()["access_token"]
                st.success("welcome back ✨", icon="🤝")
                st.rerun()
            else:
                st.error(resp.json().get("detail", "login failed"))

    with tab_signup:
        new_user = st.text_input("choose a username", key="new_user")
        new_pwd = st.text_input(
            "choose a password", type="password", key="new_pwd"
        )
        if st.button("create account", use_container_width=True):
            with st.spinner("signing up..."):
                resp = requests.post(
                    f"{API_URL}/signup",
                    json={"username": new_user, "password": new_pwd},
                )
            if resp.ok:
                st.success("account created. please log in!", icon="🙌")
            else:
                st.error(resp.json().get("detail", "couldn't create user"))

else:
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    tab1, tab2, tab3, tab4 = st.tabs(
        ["Weather", "Your favorites", "Weather Summary", "Ask about Weather"]
    )

    # ---- WEATHER TAB ----
    with tab1:
        small_text("Search for any city's weather")
        city_query = st.text_input(
            "",
            placeholder="e.g. London or Paris",
            key="search",
            label_visibility="collapsed",
        )
        get_btn = st.button("Get weather", use_container_width=True)
        if get_btn and city_query:
            with st.spinner("fetching weather..."):
                r = requests.get(
                    f"{API_URL}/weather",
                    params={"city": city_query},
                    headers=headers,
                )
            if r.ok:
                data = r.json()
                st.markdown(
                    f'<div style="padding:10px 0;font-size:1.2em;">'
                    f'<b>{data.get("city","?")}</b> · {data.get("temperature","?")}°C · {data.get("weather_condition","?")}'
                    f"</div>",
                    unsafe_allow_html=True,
                )
            else:
                st.error(r.json().get("error", "not found"))

    # ---- FAVORITES TAB ----
    with tab2:
        small_text("Your favorite cities at a glance")
        fav_resp = requests.get(f"{API_URL}/favorites", headers=headers)
        favs = fav_resp.json() if fav_resp.ok else []
        if not favs:
            small_text("no favorites yet.")
        for fav in favs:
            col1, col2 = st.columns([5, 1], gap="small")
            with col1:
                st.markdown(
                    f'<span style="font-size:1.08em;">{fav["city"]}</span> <span style="color:#aaa;">{fav["temperature"]}°C, {fav["weather_condition"]}</span>',
                    unsafe_allow_html=True,
                )
            with col2:
                if st.button("✖", key=f"rem_{fav['city']}"):
                    rem = requests.delete(
                        f"{API_URL}/favorites",
                        headers=headers,
                        json={"city": fav["city"]},
                    )
                    st.rerun()
        st.markdown("---")
        add_city = st.text_input(
            "Add city to favorites", key="addfav", placeholder="e.g. Madrid"
        )
        if st.button("add", use_container_width=True):
            r = requests.post(
                f"{API_URL}/favorites",
                headers=headers,
                json={"cities": [add_city]},
            )
            if r.ok:
                st.success("added!")
                st.rerun()
            else:
                st.error("could not add city")

    # ---- SUMMARY TAB ----
    with tab3:
        small_text("Get your waether summary ;)")
        if st.button("get summary", use_container_width=True):
            with st.spinner("thinking..."):
                resp = requests.get(f"{API_URL}/summary", headers=headers)
            if resp.ok:
                st.markdown(
                    f'<div style="font-size:1.08em;color:#aaa;">{resp.json()["summary"]}</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.error("no summary available")

    # ---- ASK WEATHER (LLM-QA) TAB ----
    with tab4:
        small_text("Ask anything about your favorites")
        ask = st.text_input(
            "your weather question",
            key="weatherq",
            placeholder="e.g. which cities are sunny now?",
        )
        if st.button("ask LLM", use_container_width=True):
            with st.spinner("the LLM is reasoning..."):
                resp = requests.post(
                    f"{API_URL}/ask", headers=headers, json={"question": ask}
                )
            if resp.ok:
                ans = resp.json()
                st.markdown(
                    f"<b>LLM:</b> {ans.get('answer', '')}",
                    unsafe_allow_html=True,
                )
                if ans.get("matchingCities"):
                    st.markdown(
                        f"<b>matching cities:</b> {', '.join(ans['matchingCities'])}",
                        unsafe_allow_html=True,
                    )
            else:
                st.error("could not get LLM answer")

    st.markdown("---")
    st.button(
        "logout",
        use_container_width=True,
        on_click=lambda: (st.session_state.pop("token", None), st.rerun()),
    )

# --- style overrides for minimalist look ---
st.markdown(
    """
    <style>
        .stTextInput>div>div>input {font-size: 1.05em;}
        .stTabs [data-baseweb="tab"] {font-size: 1em;}
        .stButton>button {font-size: 1em;padding: 0.4em 0.8em;}
        .stMarkdown {margin-bottom: 8px;}
        hr {border: none;border-top: 1px solid #eee;}
    </style>
    """,
    unsafe_allow_html=True,
)
