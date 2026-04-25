import pandas as pd
import pickle
import json
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, f1_score

from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB


def train_model():
    print("Loading dataset...")
    df = pd.read_csv("data/crops.csv")

    X = df.drop("label", axis=1)
    y = df["label"]

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled,
        y,
        test_size=0.2,
        random_state=42
    )

    models = {
        "Logistic Regression": LogisticRegression(max_iter=1000),
        "KNN": KNeighborsClassifier(),
        "Decision Tree": DecisionTreeClassifier(random_state=42),
        "Random Forest": RandomForestClassifier(random_state=42),
        "SVM": SVC(probability=True),
        "Naive Bayes": GaussianNB()
    }

    results = {}
    best_model = None
    best_model_name = ""
    best_f1 = 0

    print("Training multiple models...")

    for name, model in models.items():
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)

        accuracy = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred, average="weighted")

        results[name] = {
            "accuracy": round(accuracy * 100, 2),
            "f1_score": round(f1 * 100, 2)
        }

        print(f"{name} → Accuracy: {accuracy * 100:.2f}% | F1 Score: {f1 * 100:.2f}%")

        if f1 > best_f1:
            best_f1 = f1
            best_model = model
            best_model_name = name

    with open("model.pkl", "wb") as f:
        pickle.dump(best_model, f)

    with open("scaler.pkl", "wb") as f:
        pickle.dump(scaler, f)

    metrics = {
        "best_model": best_model_name,
        "best_f1_score": round(best_f1 * 100, 2),
        "all_models": results
    }

    with open("metrics.json", "w") as f:
        json.dump(metrics, f, indent=4)

    # Create model comparison chart
    model_names = list(results.keys())
    f1_scores = [results[name]["f1_score"] for name in model_names]

    plt.figure(figsize=(10, 6))
    plt.bar(model_names, f1_scores)
    plt.xlabel("Machine Learning Models")
    plt.ylabel("F1 Score (%)")
    plt.title("Model Comparison Based on F1 Score")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    plt.savefig("static/charts/model_comparison.png")
    plt.close()

    print("\n✅ Best Model:", best_model_name)
    print("✅ Model saved as model.pkl")
    print("✅ Scaler saved as scaler.pkl")
    print("✅ Metrics saved as metrics.json")
    print("✅ Chart saved as static/charts/model_comparison.png")


if __name__ == "__main__":
    train_model()