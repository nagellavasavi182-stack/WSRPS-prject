import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
import joblib

# Sample dataset (create if not exists)
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

# Split
X = data.drop("risk", axis=1)
y = data["risk"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Model
model = LogisticRegression()
model.fit(X_train, y_train)

# Save model
joblib.dump(model, "model.pkl")

print("Model created successfully!")