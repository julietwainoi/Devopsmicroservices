from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/", strict_slashes=False)
def products():
    return jsonify({
        "products": ["laptop", "phone", "tablet"]
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
