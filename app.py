import streamlit as st
import pandas as pd
import numpy as np
import joblib
import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap
import datetime
import geocoder

# ------------------ LOAD MODEL ------------------
model = joblib.load("model.pkl")

# ------------------ UI ------------------
st.title("🚨 Women Safety AI System")
st.markdown("### 🔐 Smart Risk Prediction + Live Tracking")
st.markdown("---")

# ------------------ LOGIN ------------------
username = st.text_input("Username")
password = st.text_input("Password", type="password")

if username == "user1" and password == "abc123":

    st.success(f"Welcome {username} 👋")

    # ------------------ AUTO LOCATION ------------------
    g = geocoder.ip('me')
    lat, lon = g.latlng

    st.success(f"📍 Your Location: {lat}, {lon}")

    # ------------------ TIME BASED RISK ------------------
    hour = datetime.datetime.now().hour

    if hour >= 20 or hour <= 5:
        st.warning("🌙 Night Time: Risk Increased")
        time_risk = 1
    else:
        st.success("☀️ Day Time: Safer")
        time_risk = 0

    # ------------------ AREA TYPE ------------------
    area_type = 1 if lat > 17 else 0
    st.write(f"📍 Area Type: {'Urban' if area_type==1 else 'Rural'}")

    # ------------------ INPUTS ------------------
    weather = st.selectbox("Weather", ["clear", "rainy", "fog"])
    crowd = st.selectbox("Crowd", ["low", "medium", "high"])
    cctv = st.selectbox("CCTV", ["yes", "no"])
    network = st.selectbox("Network", ["strong", "weak"])
    alone = st.selectbox("Alone?", ["yes", "no"])

    # Encoding
    weather = {"clear":0,"rainy":1,"fog":2}[weather]
    crowd = {"low":0,"medium":1,"high":2}[crowd]
    cctv = 1 if cctv=="yes" else 0
    network = 1 if network=="strong" else 0
    alone = 1 if alone=="yes" else 0

    # ------------------ MAP ------------------
    st.subheader("🗺️ Live Safety Map")

    m = folium.Map(location=[lat, lon], zoom_start=15)

    # User marker
    folium.Marker([lat, lon], tooltip="You are here", icon=folium.Icon(color='blue')).add_to(m)

    # ------------------ DANGER ZONES ------------------
    danger_zones = [
        [lat+0.002, lon+0.002],
        [lat-0.003, lon+0.001],
        [lat+0.001, lon-0.002]
    ]

    for d in danger_zones:
        folium.Circle(location=d, radius=300, color='red', fill=True).add_to(m)

    # Heatmap
    HeatMap(danger_zones).add_to(m)

    st_folium(m)

    # ------------------ RISK PREDICTION ------------------
    if st.button("Predict Risk"):

        input_data = np.array([[hour, area_type, 5, 2, 1, weather, crowd, cctv, 5, network, alone]])

        pred = model.predict(input_data)
        prob = model.predict_proba(input_data)[0][1]

        st.write(f"Risk Probability: {prob*100:.2f}%")

        # ------------------ RISK LEVEL ------------------
        if prob > 0.75:
            st.error("🔴 HIGH RISK AREA")

            # 🚨 EMERGENCY NOTIFICATION
            st.error(f"🚨 ALERT SENT TO {username.upper()}!")
            st.warning("📍 Share your location immediately with trusted contacts!")

        elif prob > 0.4:
            st.warning("🟡 MEDIUM RISK")

        else:
            st.success("🟢 SAFE AREA")

        # ------------------ SAVE HISTORY ------------------
        df = pd.DataFrame([[hour, prob]], columns=["time","risk"])
        df.to_csv("history.csv", mode='a', header=False, index=False)

    # ------------------ CHATBOT ------------------
    st.subheader("🤖 AI Safety Assistant")

    q = st.text_input("Ask something...")

    if q:
        if "danger" in q:
            st.write("⚠️ Avoid nearby red zones.")
        elif "night" in q:
            st.write("🌙 Stay in well-lit areas.")
        elif "help" in q:
            st.write("🚨 Call 100 immediately!")
        else:
            st.write("🤖 Stay alert and share your location.")

    # ------------------ DASHBOARD ------------------
    st.subheader("📊 Risk Dashboard")

    try:
        hist = pd.read_csv("history.csv")
        st.line_chart(hist["risk"])
    except:
        st.write("No history yet")

    # ------------------ EMERGENCY BUTTON ------------------
    if st.button("🚨 Emergency Help"):
        st.error("Emergency Alert Sent!")
        st.write(f"📍 Location: {lat}, {lon}")

else:
    st.warning("Please login with correct credentials")