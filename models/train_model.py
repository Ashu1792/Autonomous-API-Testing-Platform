import sqlite3
import pandas as pd
from sklearn.linear_model import LogisticRegression
import pickle
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score



# connect database
conn = sqlite3.connect("data/api_logs.db")

df = pd.read_sql_query("SELECT * FROM logs", conn)

conn.close()

# create failure column
df["failure"] = df["status_code"].apply(lambda x: 1 if x != 200 else 0)

X = df[["response_time"]]
y = df["failure"]

model = LogisticRegression()

model.fit(X, y)

# save model
pickle.dump(model, open("models/failure_model.pkl", "wb"))

print("Model trained successfully")

def train_model():

    conn = sqlite3.connect("data/api_logs.db")

    df = pd.read_sql_query("""
        SELECT response_time, status_code, timestamp 
        FROM logs
    """, conn)

    conn.close()

    print("Total rows:", len(df))

    # ✅ Create target
    df["failure"] = df["status_code"].apply(lambda x: 1 if x != 200 else 0)

    print("Class distribution:")
    print(df["failure"].value_counts())

    # ❗ IMPORTANT CHECK
    if len(df["failure"].unique()) < 2:
        print("Only one class found!")
        return None, 0

    # ✅ Convert time
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["hour"] = df["timestamp"].dt.hour
    df["minute"] = df["timestamp"].dt.minute

    # ✅ Features
    X = df[["response_time", "hour", "minute"]]
    y = df["failure"]

    # ✅ Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # ✅ Train
    model = RandomForestClassifier()
    model.fit(X_train, y_train)

    # ✅ Predict
    y_pred = model.predict(X_test)

    # ✅ Accuracy
    accuracy = accuracy_score(y_test, y_pred)

    print("Model Accuracy:", accuracy)

    return model, accuracy