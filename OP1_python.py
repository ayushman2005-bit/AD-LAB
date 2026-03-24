from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return "Server is running!"

@app.route('/order', methods=['POST'])
def receive_order():
    data = request.json

    print("\n===== NEW ORDER RECEIVED =====")
    print("Table:", data["table"])
    print("Customer:", data["customer"])

    for item in data["items"]:
        print(item["qty"], "x", item["name"])

    print("Instructions:", data["instructions"])
    print("==============================")

    return jsonify({"status": "ok"})

app.run(host="0.0.0.0", port=5000)
