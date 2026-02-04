from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route("/orders", methods=["POST"])
def create_order():
    token = request.headers.get("Authorization")
    auth = requests.post("http://auth-service:5000/validate", headers={"Authorization": token})
    if auth.status_code != 200:
        return {"error": "unauthorized"}, 401

    product_id = request.json.get("product_id")
    product_resp = requests.get("http://product-service:5000/products").json()
    if product_id not in range(len(product_resp["products"])):
        return {"error": "product not available"}, 400

    payment_resp = requests.post("http://payment-service:5000/pay", json={"amount": 100})
    if payment_resp.status_code != 200:
        return {"error": "payment failed"}, 400

    return jsonify({"status": "order placed", "product": product_resp["products"][product_id]})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
