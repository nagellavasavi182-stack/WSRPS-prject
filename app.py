import streamlit as st
import datetime
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

# (Optional APIs)
#from twilio.rest import Client
#import openai

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="Women Safety AI System")

# ------------------ SESSION ------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "users" not in st.session_state:
    st.session_state.users = {}
if "history" not in st.session_state:
    st.session_state.history = []

# ------------------ AUTH ------------------
def login():
    st.subheader("Login")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("Login"):
        if u in st.session_state.users and st.session_state.users[u] == p:
            st.session_state.logged_in = True
            st.success("Login Success")
        else:
            st.error("Invalid")

def signup():
    st.subheader("Sign Up")
    u = st.text_input("New Username")
    p = st.text_input("New Password", type="password")
    if st.button("Create Account"):
        st.session_state.users[u] = p
        st.success("Account Created")

# ------------------ ML MODEL ------------------
def train_model():
    # Simple dataset
    data = pd.DataFrame({
        "time": [0,1,1,0,1,0],
        "location": [0,1,1,0,1,0],
        "crowd": [0,1,0,1,1,0],
        "lighting": [0,1,1,0,1,0],
        "risk": [0,2,2,0,2,0]
    })

    X = data[["time","location","crowd","lighting"]]
    y = data["risk"]

    model = RandomForestClassifier()
    model.fit(X,y)
    return model

model = train_model()

# ------------------ SMS ALERT ------------------
def send_sms():
    # Twilio setup (replace with your keys)
    """
    client = Client("ACCOUNT_SID", "AUTH_TOKEN")
    message = client.messages.create(
        body="Emergency! Need help!",
        from_="+1234567890",
        to="+91XXXXXXXXXX"
    )
    """
    st.success("SMS Sent (Demo)")

# ------------------ CHATBOT ------------------
def chatbot_response(user_input):
    user_input = user_input.lower()

    if "safe" in user_input:
        return "Stay in well-lit and crowded areas."
    elif "help" in user_input:
        return "Call 1091 or 100 immediately."
    else:
        return "Stay alert and share your location."

# ------------------ MAIN APP ------------------
def main_app():
    menu = ["Home","Predict","Map","Emergency","Chatbot","History"]
    choice = st.sidebar.selectbox("Menu", menu)

    # HOME
    if choice == "Home":
        st.title("🚨 Women Safety AI System")
        st.write("Smart Safety Prediction System")

    # ML PREDICTION
    elif choice == "Predict":
        st.subheader("ML Risk Prediction")

        time = st.selectbox("Time", ["Day","Night"])
        location = st.selectbox("Location", ["Safe","Isolated"])
        crowd = st.selectbox("Crowd", ["Crowded","Empty"])
        lighting = st.selectbox("Lighting", ["Good","Poor"])

        # Convert to numbers
        t = 1 if time=="Night" else 0
        l = 1 if location=="Isolated" else 0
        c = 1 if crowd=="Empty" else 0
        li = 1 if lighting=="Poor" else 0

        if st.button("Predict"):
            pred = model.predict([[t,l,c,li]])[0]

            if pred == 0:
                result = "SAFE"
                st.success(result)
            elif pred == 1:
                result = "MODERATE"
                st.warning(result)
            else:
                result = "HIGH RISK"
                st.error(result)

            st.session_state.history.append((datetime.datetime.now(), result))

    # GOOGLE MAP
    elif choice == "Map":
        st.subheader("📍 Your Location")

        location = st.text_input("Enter location name")
        if location:
            st.map()  # basic map (can upgrade with API)

    # EMERGENCY
    elif choice == "Emergency":
        st.subheader("🚨 Emergency")

        st.write("Police: 100")
        st.write("Women Helpline: 1091")

        if st.button("Send SMS Alert"):
            send_sms()

    # CHATBOT
    elif choice == "Chatbot":
        st.subheader("🧠 Safety Chatbot")

        user_msg = st.text_input("Ask something")
        if st.button("Send"):
            reply = chatbot_response(user_msg)
            st.write("Bot:", reply)

    # HISTORY
    elif choice == "History":
        st.subheader("History")

        for h in st.session_state.history:
            st.write(h)

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False


# ------------------ FLOW ------------------
if not st.session_state.logged_in:
    opt = st.sidebar.selectbox("Menu", ["Login","Sign Up"])
    if opt == "Login":
        login()
    else:
        signup()
else:
    main_app()