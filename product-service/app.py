from flask import Flask, jsonify
from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)
metrics = PrometheusMetrics(app)

@app.route("/health")
def health():
    return {"status": "healthy"}, 200

@app.route("/", strict_slashes=False)
def products():
    return jsonify({
        "products": ["laptop", "phone", "tablet"]
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
