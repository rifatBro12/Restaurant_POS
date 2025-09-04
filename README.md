# Restaurant POS System

This is a Flask-based Point of Sale (POS) system tailored for a restaurant, designed to manage menu items, table assignments, orders, and sales with a modern, restaurant-themed user interface. It includes advanced features like dynamic order creation, table occupancy tracking, order status management, and sales filtering, making it a robust solution for restaurant operations.

## Features
- **Dashboard**: Displays menu item count, total completed orders, revenue, and table occupancy status, with a Chart.js bar chart showing revenue by category (Food, Drinks, Desserts).
- **Menu Management**: Add, update, or delete menu items with categories (Food, Drinks, Desserts) and availability status. Export menu data as CSV.
- **Table Management**: Add, delete, or toggle table occupancy (e.g., Free/Occupied). Tracks seat count per table and exports table data as CSV.
- **Order Placement**: Create orders with multiple items, customer names, and notes (e.g., dietary restrictions). Features dynamic item addition and real-time total calculation.
- **Order History**: View orders with filtering by status (Pending/Completed) or date, update order status, and export orders as CSV.
- **Enhanced UI**: Modern, dark-themed interface with Poppins font, gradient headers, interactive cards, and responsive design for mobile devices.
- **Data Persistence**: Stores menu, orders, and table data in CSV files (`menu.csv`, `orders.csv`, `tables.csv`).

## Project Structure
```
├── app.py          # Main Flask application with routes and logic
├── utils.py        # Helper functions for data handling and CSV operations
├── templates.py    # In-memory HTML templates for the application
├── menu.csv        # Generated file for storing menu items
├── orders.csv      # Generated file for storing order data
├── tables.csv      # Generated file for storing table data
└── README.md       # This file
```

## Prerequisites
- **Python**: Version 3.6 or higher
- **Visual Studio Code**: For development and running the application
- **Flask**: Installed via pip
- **Internet Connection**: Required for loading Chart.js and Google Fonts (Poppins) from CDNs

## Setup Instructions
Follow these steps to run the Restaurant POS system in Visual Studio Code:

1. **Create the Project Directory**:
   - Create a new directory (e.g., `restaurant_pos`).
   - Save `app.py`, `utils.py`, and `templates.py` in this directory.

2. **Open in VS Code**:
   - Launch VS Code and open the project directory (`File > Open Folder`).

3. **Set Up a Virtual Environment**:
   - Open the terminal in VS Code (`Ctrl+~` or `View > Terminal`).
   - Create a virtual environment:
     ```bash
     python -m venv venv
     ```
   - Activate the virtual environment:
     - Windows:
       ```bash
       venv\Scripts\activate
       ```
     - macOS/Linux:
       ```bash
       source venv/bin/activate
       ```

4. **Install Dependencies**:
   - Install Flask:
     ```bash
     pip install flask
     ```

5. **Run the Application**:
   - In the terminal, run:
     ```bash
     python app.py
     ```
   - The Flask development server will start at `http://127.0.0.1:5000`.

6. **Access the Application**:
   - Open a web browser and navigate to `http://127.0.0.1:5000`.
   - Use the navigation bar to access Home, Menu, Tables, Place Order, and Orders pages.

## Usage
- **Home**: View key metrics (menu items, orders, revenue, table occupancy) and a revenue chart by category.
- **Menu**: Add new menu items with name, category, price, and availability. Update prices or availability, delete items, or export the menu as CSV.
- **Tables**: Add tables with an ID and seat count, toggle occupancy status, or delete tables. Export table data as CSV.
- **Place Order**: Select a table, enter a customer name, add multiple items dynamically, and include optional notes (e.g., dietary restrictions). The system updates table occupancy and calculates totals in real-time.
- **Orders**: View all orders with details (ID, table, items, customer, status). Filter by status or date, update order status, and export orders as CSV.

## Notes
- **Templates**: Defined in-memory in `templates.py`, so no separate HTML files are needed.
- **Data Storage**: Menu, orders, and table data are stored in `menu.csv`, `orders.csv`, and `tables.csv`, created automatically in the project directory.
- **Internet Dependency**: Requires an internet connection for Chart.js and Google Fonts (Poppins) to load for the dashboard and UI styling.
- **Debug Mode**: The application runs with `debug=True` for development. Disable this in production for security.
- **Order Items**: Stored as JSON in `orders.csv` to support multiple items per order.
- **Extensibility**: The system is designed for restaurant operations but does not include advanced features like payment processing, staff management, or reservation systems, which can be added for production use.

## Troubleshooting
- **Flask Not Found**: Ensure Flask is installed in the virtual environment (`pip install flask`).
- **Port Conflict**: If port 5000 is in use, change the port: `python app.py --port 5001`.
- **CSV Files Not Created**: Verify write permissions in the project directory.
- **Chart Not Displaying**: Check your internet connection for CDN access.
- **Order Form Issues**: Ensure JavaScript is enabled in the browser for dynamic item addition and total calculation.
- **JSON Parsing Errors**: Ensure `orders.csv` is not manually edited in a way that corrupts JSON data.

## License
This project is for educational purposes and does not include a specific license. Use and modify as needed for learning or personal projects.
