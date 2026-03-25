from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
import time

app = Flask(__name__)
CORS(app)   # allow web frontend access

ORDERS_FILE = "orders.json"
MENU_FILE = "menu.json"
TABLES_FILE = "tables.json"  # Added to track table occupancy

# ---------------------------
# Utility Functions
# ---------------------------
def load_json(path, default):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return default

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=4)

def init_tables():
    """Initialize 12 free tables if the file doesn't exist."""
    if not os.path.exists(TABLES_FILE):
        # Dictionary comprehension: {"1": False, "2": False, ... "12": False}
        initial_tables = {str(i): False for i in range(1, 13)}
        save_json(TABLES_FILE, initial_tables)

# Initialize tables on startup
init_tables()

# ---------------------------
# Routes
# ---------------------------

# Test route
@app.route('/')
def home():
    return "✅ Server is running!"

# ---------------------------
# Table Management APIs (NEW)
# ---------------------------
@app.route('/tables', methods=['GET'])
def get_tables():
    """Returns the current occupied/free status of all tables."""
    tables = load_json(TABLES_FILE, {})
    return jsonify(tables)

@app.route('/tables/<int:table_id>/free', methods=['POST'])
def free_table(table_id):
    """Marks a specific table as free."""
    tables = load_json(TABLES_FILE, {})
    table_key = str(table_id)

    if table_key in tables:
        tables[table_key] = False
        save_json(TABLES_FILE, tables)
        return jsonify({
            "status": "success",
            "message": f"Table {table_id} is now free."
        })
    else:
        return jsonify({
            "status": "error",
            "message": "Invalid table ID."
        }), 400

# ---------------------------
# Receive Order (FROM ANDROID)
# ---------------------------
@app.route('/order', methods=['POST'])
def receive_order():
    data = request.json

    orders = load_json(ORDERS_FILE, [])
    tables = load_json(TABLES_FILE, {})

    # Mark the table as occupied!
    table_num = str(data.get("table"))
    tables[table_num] = True
    save_json(TABLES_FILE, tables)

    # Add extra fields
    data["id"] = len(orders) + 1
    data["status"] = "pending"
    data["time"] = time.strftime("%H:%M:%S")

    orders.append(data)
    save_json(ORDERS_FILE, orders)

    print("\n===== NEW ORDER RECEIVED =====")
    print("ID:", data["id"])
    print("Table:", data["table"])
    print("Customer:", data["customer"])

    for item in data["items"]:
        print(item["qty"], "x", item["name"])

    print("Instructions:", data.get("instructions", "None"))
    print("==============================\n")

    return jsonify({
        "status": "ok",
        "order_id": data["id"]
    })

# ---------------------------
# Get All Orders (FOR PC DASHBOARD)
# ---------------------------
@app.route('/orders', methods=['GET'])
def get_orders():
    orders = load_json(ORDERS_FILE, [])
    return jsonify(orders)

# ---------------------------
# Mark Order Completed & Auto-Free Table (THE HANDSHAKE)
# ---------------------------
@app.route('/orders/<int:order_id>/complete', methods=['POST'])
def complete_order(order_id):
    orders = load_json(ORDERS_FILE, [])
    tables = load_json(TABLES_FILE, {})

    for order in orders:
        if order["id"] == order_id:
            order["status"] = "done"

            # THE HANDSHAKE: Automatically free the table associated with this order
            table_num = str(order.get("table"))
            if table_num in tables:
                tables[table_num] = False
                print(f"✅ Handshake complete: Table {table_num} is now FREE.")

    # Save both files
    save_json(ORDERS_FILE, orders)
    save_json(TABLES_FILE, tables)

    return jsonify({"status": "completed"})

# ---------------------------
# MENU APIs (Optional Feature)
# ---------------------------

# Get Menu
@app.route('/menu', methods=['GET'])
def get_menu():
    return jsonify(load_json(MENU_FILE, []))

# Update Menu
@app.route('/menu', methods=['POST'])
def update_menu():
    data = request.json
    save_json(MENU_FILE, data)
    return jsonify({"status": "menu updated"})

# ---------------------------
# Run Server
# ---------------------------
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
