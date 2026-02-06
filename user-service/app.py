from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

@app.route("/", strict_slashes=False)
def users():
    token = request.headers.get("Authorization")
    auth = requests.post("http://auth-service:5000/validate", headers={"Authorization": token})
    if auth.status_code != 200:
        return {"error": "unauthorized"}, 401

    products = requests.get("http://product-service:5000/products/").json()
    return jsonify({
        "users": ["alice", "bob"],
        "products_visible": products["products"]
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
