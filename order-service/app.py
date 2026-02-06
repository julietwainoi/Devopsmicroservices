from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

AUTH_SERVICE = "http://auth-service:5000"
PRODUCT_SERVICE = "http://product-service:5000"
PAYMENT_SERVICE = "http://payment-service:5000"

@app.route("/", methods=["POST"], strict_slashes=False)
def create_order():
    # 1️⃣ Extract token
    token = request.headers.get("Authorization")
    if not token:
        return {"error": "missing authorization token"}, 401

    headers = {"Authorization": token}

    # 2️⃣ Validate user
    auth_resp = requests.post(f"{AUTH_SERVICE}/validate", headers=headers)
    if auth_resp.status_code != 200:
        return {"error": "unauthorized"}, 401

    # 3️⃣ Validate product
    data = request.get_json()
    if not data or "product_id" not in data:
        return {"error": "product_id required"}, 400

    product_id = data["product_id"]

    # product_resp = requests.get(f"{PRODUCT_SERVICE}/products/")
    # if product_resp.status_code != 200:
        # return {"error": "product service unavailable"}, 503
    product_resp = requests.get(f"{PRODUCT_SERVICE}/")
    if product_resp.status_code != 200:
        return {"error": "product service unavailable"}, 503

    products = product_resp.json().get("products", [])
    if product_id not in range(len(products)):
        return {"error": "product not available"}, 400

    # 4️⃣ Process payment (token forwarded)
    # payment_resp = requests.post(
        # f"{PAYMENT_SERVICE}/pay/",
        # headers=headers,
        # json={"amount": 100}
    # )
        # 4️⃣ Payment
    payment_resp = requests.post(
        f"{PAYMENT_SERVICE}/",
        headers=headers,
        json={"amount": 100}
    )
 
    if payment_resp.status_code != 200:
        return {"error": "payment failed"}, 402

    # 5️⃣ Success
    return jsonify({
        "status": "order placed",
        "product": products[product_id],
        "payment": payment_resp.json()
    }), 201


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
