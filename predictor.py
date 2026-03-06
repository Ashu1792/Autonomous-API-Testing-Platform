import pickle
import os

MODEL_PATH = "models/failure_model.pkl"

def predict_risk(response_time, status):

    # If API already failed
    if status != 200:
        return "HIGH RISK"

    # If model not trained
    if not os.path.exists(MODEL_PATH):
        return "MODEL NOT TRAINED"

    model = pickle.load(open(MODEL_PATH, "rb"))

    result = model.predict([[response_time]])

    if result[0] == 1:
        return "HIGH RISK"

    return "LOW RISK"