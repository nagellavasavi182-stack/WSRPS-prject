import streamlit as st
import pandas as pd
import numpy as np
import os
import datetime
import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap

# ------------------ SAFE IMPORTS ------------------
try:
    import joblib
except:
    import subprocess
    subprocess.run(["pip", "install", "joblib"])
    import joblib

try:
    import geocoder
except:
    import subprocess
    subprocess.run(["pip", "install", "geocoder"])
    import geocoder

# ------------------ AUTO MODEL CREATE ------------------
from sklearn.linear_model import LogisticRegression

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

    model_temp = LogisticRegression()
    model_temp.fit(X, y)

    joblib.dump(model_temp, "model.pkl")

# ------------------ LOAD MODEL ------------------
model = joblib.load("model.pkl")

# ------------------ CREATE CSV ------------------
if not os.path.exists("history.csv"):
    df = pd.DataFrame(columns=[
        "user","time","lat","lon","area_type",
        "weather","crowd","cctv","network","alone",
        "risk","result"
    ])
    df.to_csv("history.csv", index=False)

# ------------------ UI ------------------
st.title("🚨 Women Safety AI System")
st.markdown("### Smart Risk Prediction + Live Tracking")
st.markdown("---")

# ------------------ LOGIN ------------------
username = st.text_input("Username")
password = st.text_input("Password", type="password")

if username == "user1" and password == "abc123":

    st.success(f"Welcome {username}")

    # ------------------ LOCATION ------------------
    g = geocoder.ip('me')
    if g.latlng:
        lat, lon = g.latlng
    else:
        lat, lon = 17.385, 78.486  # fallback

    st.write(f"📍 Location: {lat}, {lon}")

    # ------------------ TIME ------------------
    hour = datetime.datetime.now().hour

    if hour >= 20 or hour <= 5:
        st.warning("🌙 Night Risk High")
    else:
        st.success("☀️ Day Safer")

    # ------------------ INPUT ------------------
    weather_opt = st.selectbox("Weather", ["clear","rainy","fog"])
    crowd_opt = st.selectbox("Crowd", ["low","medium","high"])
    cctv_opt = st.selectbox("CCTV", ["yes","no"])
    network_opt = st.selectbox("Network", ["strong","weak"])
    alone_opt = st.selectbox("Alone", ["yes","no"])

    # Encode
    weather = {"clear":0,"rainy":1,"fog":2}[weather_opt]
    crowd = {"low":0,"medium":1,"high":2}[crowd_opt]
    cctv = 1 if cctv_opt=="yes" else 0
    network = 1 if network_opt=="strong" else 0
    alone = 1 if alone_opt=="yes" else 0

    area_type = 1

    # ------------------ MAP ------------------
    st.subheader("🗺️ Map")

    m = folium.Map(location=[lat, lon], zoom_start=15)
    folium.Marker([lat, lon], tooltip="You").add_to(m)

    danger = [[lat+0.002,lon],[lat,lon+0.002]]

    for d in danger:
        folium.Circle(location=d, radius=300, color="red", fill=True).add_to(m)

    HeatMap(danger).add_to(m)

    st_folium(m)

    # ------------------ PREDICT ------------------
    if st.button("Predict"):

        input_data = np.array([[hour,area_type,5,2,1,weather,crowd,cctv,5,network,alone]])

        prob = model.predict_proba(input_data)[0][1]

        st.write(f"Risk: {prob*100:.2f}%")

        if prob > 0.75:
            result = "high"
            st.error("🚨 HIGH RISK ALERT!")
        elif prob > 0.4:
            result = "medium"
            st.warning("⚠️ Medium Risk")
        else:
            result = "low"
            st.success("Safe")

        # SAVE CSV
        new = pd.DataFrame([[username,hour,lat,lon,"urban",
                             weather_opt,crowd_opt,cctv_opt,
                             network_opt,alone_opt,prob,result]],
            columns=["user","time","lat","lon","area_type",
                     "weather","crowd","cctv","network","alone",
                     "risk","result"])

        new.to_csv("history.csv",mode='a',header=False,index=False)

    # ------------------ DASHBOARD ------------------
    st.subheader("📊 Dashboard")

    hist = pd.read_csv("history.csv")
    st.dataframe(hist)
    st.line_chart(hist["risk"])

else:
    st.warning("Login using user1 / abc123")