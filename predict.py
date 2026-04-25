import pickle
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

model_path = os.path.join(BASE_DIR, "model.pkl")
scaler_path = os.path.join(BASE_DIR, "scaler.pkl")

with open(model_path, "rb") as f:
    model = pickle.load(f)

with open(scaler_path, "rb") as f:
    scaler = pickle.load(f)


def predict_crop(data):
    scaled_data = scaler.transform([data])

    probabilities = model.predict_proba(scaled_data)[0]
    labels = model.classes_

    top3_indexes = probabilities.argsort()[-3:][::-1]

    results = []

    for index in top3_indexes:
        crop_name = labels[index]
        confidence = round(probabilities[index] * 100, 2)

        results.append({
            "crop": crop_name,
            "confidence": confidence
        })

    return results