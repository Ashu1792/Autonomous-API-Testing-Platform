import sqlite3
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix


def train_model():

    conn = sqlite3.connect("data/api_logs.db")

    df = pd.read_sql_query("""
        SELECT response_time, status_code, timestamp 
        FROM logs
    """, conn)

    conn.close()

    print("Total rows:", len(df))

    # ✅ Target column
    df["failure"] = df["status_code"].apply(lambda x: 1 if x != 200 else 0)

    print("Class distribution:")
    print(df["failure"].value_counts())

    # ❗ Check if both classes exist
    if len(df["failure"].unique()) < 2:
        print("Only one class found!")
        return None, 0

    # ✅ Feature engineering
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["hour"] = df["timestamp"].dt.hour
    df["minute"] = df["timestamp"].dt.minute

    # ✅ Features
    X = df[["response_time", "hour", "minute"]]
    y = df["failure"]

    # ✅ Train-test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # ✅ Model
    model = RandomForestClassifier()
    model.fit(X_train, y_train)

    # ✅ Prediction
    y_pred = model.predict(X_test)

    # ✅ Accuracy
    accuracy = accuracy_score(y_test, y_pred)
    print("Model Accuracy:", accuracy)

    # ✅ Confusion Matrix
    cm = confusion_matrix(y_test, y_pred)
    print("Confusion Matrix:\n", cm)

    return model, accuracy