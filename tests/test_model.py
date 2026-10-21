"""Model tests: training, evaluation, and serialization."""

import sys
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent / "app"
sys.path.insert(0, str(APP_DIR))

from model import MODEL_PATH, load_model, save_model, train_model  # noqa: E402


def test_train_model_returns_accuracy():
    model, accuracy, iris = train_model()
    assert model is not None
    assert 0.0 <= accuracy <= 1.0
    assert accuracy >= 0.8
    assert len(iris.feature_names) == 4


def test_model_predicts_iris_classes():
    model, _, _ = train_model()
    prediction = int(model.predict([[5.1, 3.5, 1.4, 0.2]])[0])
    assert prediction in (0, 1, 2)


def test_save_and_load_model(tmp_path):
    model, _, _ = train_model()
    path = tmp_path / "model.pkl"
    save_model(model, path)
    assert path.exists()

    loaded = load_model(path)
    assert int(loaded.predict([[5.1, 3.5, 1.4, 0.2]])[0]) == int(
        model.predict([[5.1, 3.5, 1.4, 0.2]])[0]
    )


def test_model_pkl_exists_or_can_be_created():
    if not MODEL_PATH.exists():
        model, _, _ = train_model()
        save_model(model)
    assert MODEL_PATH.exists()
