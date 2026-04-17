import streamlit as st
import pandas as pd
import numpy as np
import os
import datetime
import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap
import joblib
from sklearn.linear_model import LogisticRegression

# ---------------- UI ----------------
st.set_page_config(page_title="Women Safety risk pridiction ", layout="centered")

st.markdown("""
<style>
.title {
    font-size:30px;
    font-weight:bold;
    color:#ff4b4b;
    text-align:center;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="title">🚨 Women Safety risk pridiction' \
' System</p>', unsafe_allow_html=True)

# ---------------- MODEL ----------------
if not os.path.exists("model.pkl"):
    data = pd.DataFrame({
        "time":[22,14,20,10,23],
        "area_type":[1,1,0,1,0],
        "past_incidents":[8,2,7,1,9],
        "police_distance":[3,1,5,1,6],
        "day_type":[1,0,1,0,1],
        "weather":[1,0,2,0,1],
        "crowd_density":[0,2,0,2,0],
        "cctv_presence":[0,1,0,1,0],
        "lighting":[2,8,3,9,1],
        "network_signal":[0,1,0,1,0],
        "user_alone":[1,0,1,0,1],
        "risk":[1,0,1,0,1]
    })

    X = data.drop("risk", axis=1)
    y = data["risk"]

    model = LogisticRegression()
    model.fit(X, y)

    joblib.dump(model, "model.pkl")

model = joblib.load("model.pkl")

# ---------------- LOGIN ----------------
st.subheader("🔐 Login")

username = st.text_input("Username")
password = st.text_input("Password", type="password")

if username == "user1" and password == "abc123":

    st.success("Login Successful ✅")

    # ---------------- LOCATION ----------------
    lat, lon = 17.385, 78.486
    st.write(f"📍 Location: {lat}, {lon}")

    hour = datetime.datetime.now().hour

    # ---------------- INPUT ----------------
    weather_opt = st.selectbox("Weather", ["clear","rainy","fog"])
    crowd_opt = st.selectbox("Crowd", ["low","medium","high"])

    weather = {"clear":0,"rainy":1,"fog":2}[weather_opt]
    crowd = {"low":0,"medium":1,"high":2}[crowd_opt]

    # ---------------- MAP ----------------
    st.subheader("🗺️ Live Map")

    m = folium.Map(location=[lat, lon], zoom_start=15)
    folium.Marker([lat, lon], tooltip="You").add_to(m)

    danger = [[lat+0.002, lon], [lat, lon+0.002]]

    for d in danger:
        folium.Circle(location=d, radius=300, color="red", fill=True).add_to(m)

    HeatMap(danger).add_to(m)

    st_folium(m)

    # ---------------- PREDICT ----------------
    if st.button("🔍 Predict Risk"):

        input_data = np.array([[hour,1,5,2,1,weather,crowd,1,5,1,1]])

        prob = model.predict_proba(input_data)[0][1]

        st.subheader("📊 Risk Analysis")
        st.metric("Risk %", f"{prob*100:.2f}")

        if prob > 0.75:
            st.error("🚨 HIGH RISK AREA")
            risk_level = "High"
        elif prob > 0.4:
            st.warning("⚠️ MEDIUM RISK")
            risk_level = "Medium"
        else:
            st.success("🟢 SAFE AREA")
            risk_level = "Low"

    # ---------------- CHATBOT ----------------
    st.subheader("🤖 AI Safety Chatbot")

    user_q = st.text_input("Ask Safety Assistant")

    if user_q:

        q = user_q.lower()

        if "help" in q or "emergency" in q:
            st.error("🚨 Call 100 immediately or contact nearby police station.")
        elif "safe" in q:
            st.info("Always avoid isolated places at night and share location with family.")
        elif "night" in q:
            st.warning("🌙 Night time is high risk. Stay in well-lit areas.")
        elif "danger" in q:
            st.warning("⚠️ Avoid red zones shown in map.")
        else:
            st.success("I am your safety assistant. Ask about safety, emergency, or risk.")

    # ---------------- HISTORY ----------------
    if st.button("Save Record"):

        new = pd.DataFrame([[username,hour,lat,lon,prob]],
                           columns=["user","time","lat","lon","risk"])

        if os.path.exists("history.csv"):
            new.to_csv("history.csv", mode='a', header=False, index=False)
        else:
            new.to_csv("history.csv", index=False)

        st.success("Saved ✅")

else:
    st.warning("Login: user1 / abc123")