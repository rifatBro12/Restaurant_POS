from flask import Flask, render_template, request, send_file
from jinja2 import DictLoader
from utils import load_menu, load_orders, load_tables, save_menu, save_orders, save_tables, generate_order_id, menu, orders, tables
from templates import base_template, home_template, menu_template, tables_template, order_template, orders_template
from collections import defaultdict
from datetime import datetime

app = Flask(__name__)

# Register in-memory templates
app.jinja_loader = DictLoader({
    "base.html": base_template,
    "home.html": home_template,
    "menu.html": menu_template,
    "tables.html": tables_template,
    "order.html": order_template,
    "orders.html": orders_template,
})

# Routes
@app.route("/")
def home():
    sales_summary = defaultdict(float)
    for o in orders:
        if o[5] == "Completed":
            sales_summary[menu[list(o[3].keys())[0]]["category"] if o[3] else "Unknown"] += o[2]
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

# Startup
if __name__ == "__main__":
    load_menu()
    load_orders()
    load_tables()
    app.run(debug=True)