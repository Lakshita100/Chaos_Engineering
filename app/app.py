"""Flask prediction API for the Iris classifier.

Endpoints:
    GET  /        -> Service running page (with prediction form)
    GET  /health  -> {"status": "healthy"}
    POST /predict -> Prediction for {"features": [f1, f2, f3, f4]}
"""

import sys
from pathlib import Path

from flask import Flask, jsonify, render_template_string, request

APP_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = APP_DIR.parent
sys.path.insert(0, str(APP_DIR))

from model import MODEL_PATH, load_model, save_model, train_model  # noqa: E402

app = Flask(__name__)

IRIS_CLASSES = ["setosa", "versicolor", "virginica"]

INDEX_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>ResilAI - Iris Prediction Service</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 40px; background: #f7f9fc; }
    .card { background: #fff; padding: 24px; border-radius: 8px;
            max-width: 520px; box-shadow: 0 2px 6px rgba(0,0,0,.1); }
    label { display: block; margin-top: 10px; }
    input { width: 100%; padding: 6px; box-sizing: border-box; }
    button { margin-top: 16px; padding: 8px 18px; cursor: pointer; }
    #result { margin-top: 16px; font-weight: bold; }
    #status { color: #1a7f37; }
  </style>
</head>
<body>
  <div class="card">
    <h1>ResilAI Prediction Service</h1>
    <p id="status">Service running. Status: {{ status }}</p>
    <form id="predict-form">
      <label>Sepal length (cm)</label><input id="f0" type="number" step="0.1" value="5.1" required>
      <label>Sepal width (cm)</label><input id="f1" type="number" step="0.1" value="3.5" required>
      <label>Petal length (cm)</label><input id="f2" type="number" step="0.1" value="1.4" required>
      <label>Petal width (cm)</label><input id="f3" type="number" step="0.1" value="0.2" required>
      <button id="predict-btn" type="submit">Predict</button>
    </form>
    <p id="result"></p>
  </div>
  <script>
    document.getElementById('predict-form').addEventListener('submit', async (e) => {
      e.preventDefault();
      const features = [0, 1, 2, 3].map(i => parseFloat(document.getElementById('f' + i).value));
      const res = await fetch('/predict', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({features: features})
      });
      const data = await res.json();
      const el = document.getElementById('result');
      if (res.ok) {
        el.style.color = '#1a7f37';
        el.textContent = 'Prediction: ' + data.prediction + ' (' + data.class_name + ')';
      } else {
        el.style.color = '#b42318';
        el.textContent = 'Error: ' + (data.error || 'prediction failed');
      }
    });
  </script>
</body>
</html>
"""


def get_model():
    """Load the model, training it first if model.pkl does not exist."""
    if not MODEL_PATH.exists():
        model, _, _ = train_model()
        save_model(model)
    return load_model()


model = get_model()


@app.route("/")
def index():
    return render_template_string(INDEX_HTML, status="running")


@app.route("/health")
def health():
    return jsonify({"status": "healthy"})


@app.route("/predict", methods=["POST"])
def predict():
    if not request.is_json or request.get_json(silent=True) is None:
        return jsonify({"error": "Request body must be valid JSON"}), 400

    data = request.get_json()
    if "features" not in data:
        return jsonify({"error": "Missing required field: features"}), 400

    features = data["features"]
    if not isinstance(features, (list, tuple)):
        return jsonify({"error": "features must be a list of numbers"}), 400
    if len(features) != 4:
        return jsonify({"error": "features must contain exactly 4 values"}), 400

    try:
        values = [float(v) for v in features]
    except (TypeError, ValueError):
        return jsonify({"error": "features must contain only numeric values"}), 400

    prediction_id = int(model.predict([values])[0])
    return jsonify(
        {
            "prediction": prediction_id,
            "class_name": IRIS_CLASSES[prediction_id],
            "features": values,
        }
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
