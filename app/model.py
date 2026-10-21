"""ML model training: Iris dataset + Random Forest classifier.

Workflow:
    Load Dataset -> Split Data -> Train Random Forest -> Evaluate -> Save model.pkl
"""

from pathlib import Path

import joblib
import pandas as pd
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

MODEL_PATH = Path(__file__).resolve().parent.parent / "model" / "model.pkl"


def train_model(random_state: int = 42):
    """Train a Random Forest classifier on the Iris dataset."""
    iris = load_iris()
    X = pd.DataFrame(iris.data, columns=iris.feature_names)
    y = pd.Series(iris.target)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=random_state, stratify=y
    )

    model = RandomForestClassifier(n_estimators=100, random_state=random_state)
    model.fit(X_train, y_train)

    accuracy = accuracy_score(y_test, model.predict(X_test))
    return model, accuracy, iris


def save_model(model, path: Path = MODEL_PATH) -> Path:
    """Serialize the trained model to model/model.pkl."""
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, path)
    return path


def load_model(path: Path = MODEL_PATH):
    """Load a previously saved model."""
    return joblib.load(path)


if __name__ == "__main__":
    model, accuracy, iris = train_model()
    saved = save_model(model)
    print(f"Model trained. Accuracy: {accuracy:.4f}")
    print(f"Classes: {list(iris.target_names)}")
    print(f"Model saved to: {saved}")
