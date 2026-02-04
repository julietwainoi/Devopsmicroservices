from flask import Flask, request, jsonify
import jwt
import datetime

app = Flask(__name__)
SECRET_KEY = "devops-secret"

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if username == "admin" and password == "password":
        token = jwt.encode({
            "user": username,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
        }, SECRET_KEY, algorithm="HS256")
        return jsonify({"token": token})

    return jsonify({"error": "invalid credentials"}), 401

@app.route("/validate", methods=["POST"])
def validate():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    try:
        jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return jsonify({"status": "valid"})
    except Exception:
        return jsonify({"status": "invalid"}), 401

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
