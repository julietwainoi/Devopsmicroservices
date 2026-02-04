from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/pay", methods=["POST"])
def pay():
    data = request.json
    amount = data.get("amount")
    if amount <= 0:
        return {"status": "failed"}, 400
    return {"status": "success"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
