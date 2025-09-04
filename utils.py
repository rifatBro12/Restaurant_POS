import csv
import random
import string
import os
import json

menu_file = "menu.csv"
orders_file = "orders.csv"
tables_file = "tables.csv"

menu = {}
orders = []
tables = {}

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