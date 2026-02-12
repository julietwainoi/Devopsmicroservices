
from flask import Flask, request, jsonify
import requests
from db import get_connection
from psycopg2.extras import Json



app = Flask(__name__)

AUTH_SERVICE = "http://auth-service:5000"
PRODUCT_SERVICE = "http://product-service:5000"
PAYMENT_SERVICE = "http://payment-service:5000"

@app.route("/health")
def health():
    try:
        conn = get_connection()
        conn.close()
        return {"status": "ok"}, 200
    except Exception:
        return {"status": "unhealthy"}, 500


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

    product_resp = requests.get(f"{PRODUCT_SERVICE}/")
    if product_resp.status_code != 200:
        return {"error": "product service unavailable"}, 503

    products = product_resp.json().get("products", [])
    
       # FIX: Check bounds properly and assign selected_product
    if not isinstance(products, list) or product_id >= len(products) or product_id < 0:
        return {"error": "product not available"}, 400
  
    selected_product = products[product_id]
 

        # 4️⃣ Payment
    payment_resp = requests.post(
        f"{PAYMENT_SERVICE}/",
        headers=headers,
        json={"amount": 100}
    )
 
    if payment_resp.status_code != 200:
        return {"error": "payment failed"}, 402

    # 5️⃣ Success
    # return jsonify({
        # "status": "order placed",
        # "product": products[product_id],
        # "payment": payment_resp.json()
    # }), 201
    # 5️⃣ Save order to database (ONLY after payment success)
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO orders (product, status)
            VALUES (%s, %s)
            RETURNING id
            """,
            (Json(selected_product), "PAID")
        )

        order_id = cur.fetchone()[0]
        conn.commit()

        cur.close()
        conn.close()

    except Exception as e:
        return {"error": "database error", "details": str(e)}, 500

    # 6️⃣ Success response
    return jsonify({
        "status": "order placed",
        "order_id": order_id,
        "product": selected_product,
        "payment": payment_resp.json()
    }), 201



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
