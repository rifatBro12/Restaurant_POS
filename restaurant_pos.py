from flask import Flask, render_template, request, send_file
from jinja2 import DictLoader
import csv
import random
import string
import os
from collections import defaultdict
from datetime import datetime, timedelta
import json

app = Flask(__name__)

# -------------------------
# Data
# -------------------------
menu_file = "menu.csv"
orders_file = "orders.csv"
tables_file = "tables.csv"

menu = {}
orders = []
tables = {}

# -------------------------
# Helpers
# -------------------------
def load_menu():
    global menu
    if os.path.exists(menu_file):
        with open(menu_file, mode="r", newline="") as f:
            reader = csv.reader(f)
            for row in reader:
                if row:
                    menu[row[0]] = {
                        "category": row[1],
                        "price": float(row[2]),
                        "available": row[3] == "True"
                    }

def load_orders():
    global orders
    orders = []
    if os.path.exists(orders_file):
        with open(orders_file, mode="r", newline="") as f:
            reader = csv.reader(f)
            for row in reader:
                if row:
                    items = json.loads(row[3]) if row[3] else {}
                    orders.append([row[0], row[1], float(row[2]), items, row[4], row[5]])

def load_tables():
    global tables
    if os.path.exists(tables_file):
        with open(tables_file, mode="r", newline="") as f:
            reader = csv.reader(f)
            for row in reader:
                if row:
                    tables[row[0]] = {"seats": int(row[1]), "occupied": row[2] == "True"}

def save_menu():
    with open(menu_file, mode="w", newline="") as f:
        writer = csv.writer(f)
        for name, data in menu.items():
            writer.writerow([name, data["category"], data["price"], data["available"]])

def save_orders():
    with open(orders_file, mode="w", newline="") as f:
        writer = csv.writer(f)
        for order in orders:
            writer.writerow([order[0], order[1], order[2], json.dumps(order[3]), order[4], order[5]])

def save_tables():
    with open(tables_file, mode="w", newline="") as f:
        writer = csv.writer(f)
        for table_id, data in tables.items():
            writer.writerow([table_id, data["seats"], data["occupied"]])

def generate_order_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

# -------------------------
# Templates
# -------------------------
base_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Restaurant POS System</title>
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap">
    <style>
        body {
            font-family: 'Poppins', sans-serif;
            background: #1a1a1a;
            color: #f0f0f0;
            margin: 0;
            padding: 0;
        }
        header {
            background: linear-gradient(to right, #c8102e, #f4a261);
            color: white;
            padding: 1.5rem;
            text-align: center;
            position: sticky;
            top: 0;
            z-index: 1000;
            box-shadow: 0 2px 5px rgba(0,0,0,0.3);
        }
        nav a {
            margin: 0 20px;
            color: white;
            text-decoration: none;
            font-weight: 600;
            transition: color 0.3s ease;
        }
        nav a:hover {
            color: #ffdd57;
        }
        .container {
            width: 90%;
            max-width: 1200px;
            margin: 2rem auto;
            background: #2c2c2c;
            padding: 2rem;
            border-radius: 12px;
            box-shadow: 0 6px 15px rgba(0,0,0,0.5);
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 1rem;
        }
        th, td {
            padding: 12px;
            border-bottom: 1px solid #444;
            text-align: left;
        }
        th {
            background: #c8102e;
            color: white;
        }
        .btn {
            padding: 10px 20px;
            margin: 6px 0;
            background: #f4a261;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s ease;
            font-weight: 600;
        }
        .btn:hover {
            background: #e68a3c;
            transform: scale(1.05);
        }
        .btn-danger {
            background: #d00000;
        }
        .btn-danger:hover {
            background: #a00000;
            transform: scale(1.05);
        }
        .success, .error {
            font-weight: bold;
            padding: 10px;
            border-radius: 6px;
            animation: fadeIn 0.5s ease-in-out;
        }
        .success { background: #2a9d8f; color: white; }
        .error { background: #d00000; color: white; }
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        .menu-grid, .table-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
            gap: 1.5rem;
        }
        .card {
            background: #3a3a3a;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 6px 12px rgba(0,0,0,0.3);
            text-align: center;
            transition: transform 0.3s ease;
        }
        .card:hover {
            transform: translateY(-5px);
        }
        input, select, textarea {
            padding: 10px;
            margin: 6px 0;
            background: #444;
            color: #f0f0f0;
            border: 1px solid #666;
            border-radius: 6px;
            width: calc(100% - 22px);
        }
        .filter-form {
            display: flex;
            gap: 1rem;
            flex-wrap: wrap;
        }
        .filter-form select, .filter-form input {
            width: auto;
            min-width: 150px;
        }
        @media (max-width: 768px) {
            .container {
                width: 95%;
            }
            nav a {
                display: block;
                margin: 12px 0;
            }
            .filter-form {
                flex-direction: column;
            }
        }
    </style>
</head>
<body>
    <header>
        <h1>Restaurant POS System</h1>
        <nav>
            <a href="{{ url_for('home') }}">Home</a>
            <a href="{{ url_for('manage_menu') }}">Menu</a>
            <a href="{{ url_for('manage_tables') }}">Tables</a>
            <a href="{{ url_for('place_order') }}">Place Order</a>
            <a href="{{ url_for('view_orders') }}">Orders</a>
        </nav>
    </header>
    <div class="container">
        {% block content %}{% endblock %}
    </div>
</body>
</html>
"""

home_template = """
{% extends "base.html" %}
{% block content %}
    <h2>Welcome to the Restaurant POS</h2>
    <p>Manage your restaurant's menu, tables, and orders with ease.</p>
    <h3>Dashboard</h3>
    <p>Menu Items: {{ num_items }}</p>
    <p>Total Orders: {{ total_orders }}</p>
    <p>Total Revenue: ${{ "%.2f"|format(total_revenue) }}</p>
    <p>Occupied Tables: {{ occupied_tables }} / {{ total_tables }}</p>
    {% if labels %}
    <canvas id="myChart" width="600" height="300"></canvas>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script>
    var ctx = document.getElementById('myChart').getContext('2d');
    var myChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: {{ labels | tojson }},
            datasets: [{
                label: 'Revenue by Category',
                data: {{ data | tojson }},
                backgroundColor: 'rgba(244, 162, 97, 0.4)',
                borderColor: 'rgba(244, 162, 97, 1)',
                borderWidth: 2
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true,
                    grid: { color: '#666' }
                },
                x: {
                    grid: { color: '#666' }
                }
            },
            plugins: {
                legend: { labels: { color: '#f0f0f0' } }
            }
        }
    });
    </script>
    {% endif %}
{% endblock %}
"""

menu_template = """
{% extends "base.html" %}
{% block content %}
    <h2>Menu Management</h2>
    <form method="post">
        <input type="text" name="name" placeholder="Item Name" required>
        <select name="category" required>
            <option value="Food">Food</option>
            <option value="Drinks">Drinks</option>
            <option value="Desserts">Desserts</option>
        </select>
        <input type="number" step="0.01" name="price" placeholder="Price" required>
        <label><input type="checkbox" name="available" checked> Available</label>
        <button class="btn" type="submit">Add Item</button>
    </form>
    <br>
    <div class="menu-grid">
        {% for name, data in menu.items() %}
        <div class="card">
            <h3>{{ name }}</h3>
            <p>Category: {{ data.category }}</p>
            <p>Price: ${{ "%.2f"|format(data.price) }}</p>
            <p>Status: {{ 'Available' if data.available else 'Unavailable' }}</p>
            <form method="post">
                <input type="hidden" name="action" value="update">
                <input type="hidden" name="name" value="{{ name }}">
                <input type="number" step="0.01" name="price" value="{{ "%.2f"|format(data.price) }}" required>
                <label><input type="checkbox" name="available" {{ 'checked' if data.available else '' }}> Available</label>
                <button type="submit" class="btn">Update</button>
            </form>
            <form method="post">
                <input type="hidden" name="action" value="delete">
                <input type="hidden" name="name" value="{{ name }}">
                <button type="submit" class="btn btn-danger">Delete</button>
            </form>
        </div>
        {% endfor %}
    </div>
    <br>
    <a class="btn" href="{{ url_for('export_menu') }}">Export Menu CSV</a>
{% endblock %}
"""

tables_template = """
{% extends "base.html" %}
{% block content %}
    <h2>Table Management</h2>
    <form method="post">
        <input type="text" name="table_id" placeholder="Table ID (e.g., T1)" required>
        <input type="number" name="seats" placeholder="Number of Seats" required>
        <button class="btn" type="submit">Add Table</button>
    </form>
    <br>
    <div class="table-grid">
        {% for table_id, data in tables.items() %}
        <div class="card">
            <h3>Table {{ table_id }}</h3>
            <p>Seats: {{ data.seats }}</p>
            <p>Status: {{ 'Occupied' if data.occupied else 'Free' }}</p>
            <form method="post">
                <input type="hidden" name="action" value="toggle">
                <input type="hidden" name="table_id" value="{{ table_id }}">
                <button type="submit" class="btn {{ 'btn-danger' if data.occupied else '' }}">
                    {{ 'Free Table' if data.occupied else 'Occupy Table' }}
                </button>
            </form>
            <form method="post">
                <input type="hidden" name="action" value="delete">
                <input type="hidden" name="table_id" value="{{ table_id }}">
                <button type="submit" class="btn btn-danger">Delete</button>
            </form>
        </div>
        {% endfor %}
    </div>
    <br>
    <a class="btn" href="{{ url_for('export_tables') }}">Export Tables CSV</a>
{% endblock %}
"""

order_template = """
{% extends "base.html" %}
{% block content %}
    <h2>Place Order</h2>
    <form method="post">
        <select name="table_id" required>
            {% for table_id, data in tables.items() %}
            <option value="{{ table_id }}">Table {{ table_id }} ({{ data.seats }} seats, {{ 'Occupied' if data.occupied else 'Free' }})</option>
            {% endfor %}
        </select>
        <input type="text" name="customer_name" placeholder="Customer Name" required>
        <textarea name="notes" placeholder="Order Notes (e.g., dietary restrictions)"></textarea>
        <h3>Order Items</h3>
        <div id="items">
            <div class="item-row">
                <select name="items[0][name]" required>
                    {% for name in menu.keys() %}
                    {% if menu[name].available %}
                    <option value="{{ name }}">{{ name }} ({{ menu[name].category }})</option>
                    {% endif %}
                    {% endfor %}
                </select>
                <input type="number" name="items[0][quantity]" min="1" value="1" required>
            </div>
        </div>
        <button type="button" class="btn" onclick="addItem()">Add Item</button>
        <button class="btn" type="submit">Place Order</button>
    </form>
    <p id="total">Total: $0.00</p>
    {% if message %}
        <p class="{{ 'success' if 'Order' in message else 'error' }}">{{ message }}</p>
    {% endif %}
    <script>
    var menu = {{ menu | tojson }};
    var itemCount = 1;
    function addItem() {
        var div = document.createElement('div');
        div.className = 'item-row';
        div.innerHTML = `
            <select name="items[${itemCount}][name]" required>
                {% for name in menu.keys() %}
                {% if menu[name].available %}
                <option value="{{ name }}">{{ name }} ({{ menu[name].category }})</option>
                {% endif %}
                {% endfor %}
            </select>
            <input type="number" name="items[${itemCount}][quantity]" min="1" value="1" required>
        `;
        document.getElementById('items').appendChild(div);
        itemCount++;
        updateTotal();
    }
    function updateTotal() {
        var total = 0;
        document.querySelectorAll('.item-row').forEach(row => {
            var name = row.querySelector('select').value;
            var qty = parseInt(row.querySelector('input').value) || 1;
            total += (menu[name]?.price || 0) * qty;
        });
        document.getElementById('total').innerHTML = 'Total: $' + total.toFixed(2);
    }
    document.getElementById('items').addEventListener('change', updateTotal);
    document.getElementById('items').addEventListener('input', updateTotal);
    updateTotal();
    </script>
{% endblock %}
"""

orders_template = """
{% extends "base.html" %}
{% block content %}
    <h2>Order History</h2>
    <form class="filter-form" method="get">
        <select name="status">
            <option value="">All Statuses</option>
            <option value="Pending">Pending</option>
            <option value="Completed">Completed</option>
        </select>
        <input type="date" name="date">
        <button class="btn" type="submit">Filter</button>
    </form>
    <br>
    <table>
        <tr><th>Order ID</th><th>Table</th><th>Total</th><th>Items</th><th>Customer</th><th>Status</th><th>Actions</th></tr>
        {% for order in orders %}
        <tr>
            <td>{{ order[0] }}</td>
            <td>{{ order[1] }}</td>
            <td>${{ "%.2f"|format(order[2]) }}</td>
            <td>
                {% for name, qty in order[3].items() %}
                {{ name }} (x{{ qty }})<br>
                {% endfor %}
            </td>
            <td>{{ order[4] }}</td>
            <td>{{ order[5] }}</td>
            <td>
                <form method="post" style="display:inline;">
                    <input type="hidden" name="action" value="update_status">
                    <input type="hidden" name="order_id" value="{{ order[0] }}">
                    <select name="status">
                        <option value="Pending" {{ 'selected' if order[5] == 'Pending' else '' }}>Pending</option>
                        <option value="Completed" {{ 'selected' if order[5] == 'Completed' else '' }}>Completed</option>
                    </select>
                    <button type="submit" class="btn">Update</button>
                </form>
            </td>
        </tr>
        {% endfor %}
    </table>
    <p>Total Revenue: ${{ "%.2f"|format(total) }}</p>
    <br>
    <a class="btn" href="{{ url_for('export_orders') }}">Export Orders CSV</a>
{% endblock %}
"""

# -------------------------
# Register templates
# -------------------------
app.jinja_loader = DictLoader({
    "base.html": base_template,
    "home.html": home_template,
    "menu.html": menu_template,
    "tables.html": tables_template,
    "order.html": order_template,
    "orders.html": orders_template,
})

# -------------------------
# Routes
# -------------------------
@app.route("/")
def home():
    sales_summary = defaultdict(float)
    for o in orders:
        if o[5] == "Completed":
            sales_summary[menu[o[3].keys()[0]]["category"] if o[3] else "Unknown"] += o[2]
    labels = list(sales_summary.keys())
    data = list(sales_summary.values())
    num_items = len(menu)
    total_orders = len([o for o in orders if o[5] == "Completed"])
    total_revenue = sum(data)
    total_tables = len(tables)
    occupied_tables = sum(1 for t in tables.values() if t["occupied"])
    return render_template("home.html", num_items=num_items, total_orders=total_orders, total_revenue=total_revenue, occupied_tables=occupied_tables, total_tables=total_tables, labels=labels, data=data)

@app.route("/menu", methods=["GET", "POST"])
def manage_menu():
    if request.method == "POST":
        action = request.form.get("action")
        if action == "delete":
            name = request.form["name"]
            if name in menu:
                del menu[name]
                save_menu()
        elif action == "update":
            name = request.form["name"]
            price = float(request.form["price"])
            available = request.form.get("available") == "on"
            if name in menu:
                menu[name].update({"price": price, "available": available})
                save_menu()
        else:
            name = request.form["name"]
            category = request.form["category"]
            price = float(request.form["price"])
            available = request.form.get("available") == "on"
            menu[name] = {"category": category, "price": price, "available": available}
            save_menu()
    return render_template("menu.html", menu=menu)

@app.route("/tables", methods=["GET", "POST"])
def manage_tables():
    if request.method == "POST":
        action = request.form.get("action")
        if action == "delete":
            table_id = request.form["table_id"]
            if table_id in tables:
                del tables[table_id]
                save_tables()
        elif action == "toggle":
            table_id = request.form["table_id"]
            if table_id in tables:
                tables[table_id]["occupied"] = not tables[table_id]["occupied"]
                save_tables()
        else:
            table_id = request.form["table_id"]
            seats = int(request.form["seats"])
            tables[table_id] = {"seats": seats, "occupied": False}
            save_tables()
    return render_template("tables.html", tables=tables)

@app.route("/order", methods=["GET", "POST"])
def place_order():
    message = None
    if request.method == "POST":
        table_id = request.form["table_id"]
        customer_name = request.form["customer_name"]
        notes = request.form.get("notes", "")
        items = {}
        for key, value in request.form.items():
            if key.startswith("items[") and key.endswith("[name]"):
                idx = key.split("[")[1].split("]")[0]
                qty_key = f"items[{idx}][quantity]"
                item_name = value
                item_qty = int(request.form.get(qty_key, 1))
                if item_name in menu and menu[item_name]["available"]:
                    items[item_name] = item_qty
        if not items:
            message = "Error: No valid items selected."
        elif table_id not in tables:
            message = "Error: Invalid table ID."
        else:
            total = sum(menu[name]["price"] * qty for name, qty in items.items())
            order_id = generate_order_id()
            orders.append([order_id, table_id, total, items, customer_name, "Pending"])
            if not tables[table_id]["occupied"]:
                tables[table_id]["occupied"] = True
            save_orders()
            save_tables()
            message = f"Order {order_id} placed for Table {table_id}. Total: ${total:.2f}"
    return render_template("order.html", menu=menu, tables=tables, message=message)

@app.route("/orders", methods=["GET", "POST"])
def view_orders():
    filtered_orders = orders
    if request.method == "GET" and (request.args.get("status") or request.args.get("date")):
        status = request.args.get("status")
        date = request.args.get("date")
        filtered_orders = [
            o for o in orders
            if (not status or o[5] == status) and
               (not date or o[0].startswith(date.replace("-", "")))
        ]
    elif request.method == "POST":
        action = request.form.get("action")
        if action == "update_status":
            order_id = request.form["order_id"]
            new_status = request.form["status"]
            for order in orders:
                if order[0] == order_id:
                    order[5] = new_status
                    if new_status == "Completed" and order[1] in tables:
                        tables[order[1]]["occupied"] = False
                    save_orders()
                    save_tables()
                    break
    total = sum(o[2] for o in filtered_orders if o[5] == "Completed")
    return render_template("orders.html", orders=filtered_orders, total=total)

@app.route("/export/menu")
def export_menu():
    return send_file("menu.csv", as_attachment=True)

@app.route("/export/tables")
def export_tables():
    return send_file("tables.csv", as_attachment=True)

@app.route("/export/orders")
def export_orders():
    return send_file("orders.csv", as_attachment=True)

# -------------------------
# Startup
# -------------------------
if __name__ == "__main__":
    load_menu()
    load_orders()
    load_tables()
    app.run(debug=True)