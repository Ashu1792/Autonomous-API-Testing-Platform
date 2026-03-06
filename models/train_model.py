import sqlite3
import pandas as pd
from sklearn.linear_model import LogisticRegression
import pickle

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