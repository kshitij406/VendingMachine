import sqlite3
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend for generating plots in background
import base64
from io import BytesIO

# Represents a product with id, name, price, and available stock
class Product:
    def __init__(self, id, name, price, stock):
        self.id = id
        self.name = name
        self.price = price
        self.stock = stock

    def __str__(self):
        return f"Product: {self.name}, Price: ${self.price:.2f}, Stock: {self.stock}"

# Handles operations related to shopping cart
class Cart:
    def __init__(self):
        # Cart items: key = productID, value = Product object holding quantity and total price
        self.cart = {}

    # Add a product to the cart if stock is sufficient
    def add_item(self, product_id, quantity, inventory):
        if product_id in inventory:
            product = inventory[product_id]

            if product.stock >= quantity:
                product.stock -= quantity  # Decrement from inventory stock

                if product_id not in self.cart:
                    # Store new item in cart
                    self.cart[product_id] = Product(product_id, product.name, product.price * quantity, quantity)
                else:
                    # Update existing item in cart
                    existing = self.cart[product_id]
                    existing.stock += quantity
                    existing.price += product.price * quantity

                return f"{quantity} units of '{product.name}' added to cart."
            else:
                return "Not enough stock."
        else:
            return f"Product ID '{product_id}' does not exist."

    # Remove a quantity of item from cart, and restore to inventory
    def remove_item(self, product_id, quantity, inventory):
        if product_id not in self.cart:
            return f"Product ID '{product_id}' is not in the cart."

        cart_item = self.cart[product_id]

        if quantity >= cart_item.stock:
            removed_quantity = cart_item.stock
            del self.cart[product_id]
        else:
            cart_item.stock -= quantity
            cart_item.price -= inventory[product_id].price * quantity
            removed_quantity = quantity

        inventory[product_id].stock += removed_quantity
        return f"{removed_quantity} units of '{inventory[product_id].name}' removed from cart."

    # Display the cart contents
    def view_items(self):
        if not self.cart:
            return "Cart is empty."
        output = "Cart:\n"
        output += f"{'ProductID':<10} {'Name':<30} {'Total':<10} {'Qty':<6}\n"
        output += "-" * 50 + "\n"
        for pid, product in self.cart.items():
            output += f"{pid:<10} {product.name:<30} ${product.price:<9.2f} {product.stock:<6}\n"
        return output

    def calculate_total(self):
        return sum(product.price for product in self.cart.values())

    def clear_cart(self):
        if self.cart:
            self.cart.clear()
            print("The cart was cleared.")
        else:
            print("The cart is already empty.")

# Manages the vending machine: inventory, transactions, database interaction
class VendingMachine:
    def __init__(self):
        self.inventory = self.load_inventory()

    # Load all products from the SQLite DB into memory
    def load_inventory(self):
        conn = sqlite3.connect("vending_machine.db")
        cur = conn.cursor()
        cur.execute("SELECT * FROM Products")
        products = cur.fetchall()
        conn.close()

        inventory = {}
        for product in products:
            pid, name, price, stock = product
            inventory[pid] = Product(pid, name, float(price), int(stock))
        return inventory

    # Display all available products with formatting
    def display_products(self):
        self.inventory = self.load_inventory()
        message = f"{'ProductID':<10} {'Name':<30} {'Price':<10} {'Stock':<6}\n"
        message += "-" * 70 + "\n"
        for pid, product in self.inventory.items():
            message += f"{pid:<10} {product.name:<30} ${product.price:<9.2f} {product.stock:<6}\n"
        return message

    # Generate a receipt from cart items
    def generate_receipt(self, cart):
        receipt = "\n" + "=" * 80 + "\n"
        receipt += " " * 12 + "PURCHASE RECEIPT\n"
        receipt += "=" * 40 + "\n"
        receipt += f"{'ProductID':<10} {'Name':<15} {'Qty':<5} {'Total':<8}\n"
        receipt += "-" * 40 + "\n"
        for pid, product in cart.cart.items():
            receipt += f"{pid:<10} {product.name:<15} {product.stock:<5} ${product.price:<7.2f}\n"
        receipt += "-" * 40 + "\n"
        receipt += f"{'TOTAL':>32} : ${cart.calculate_total():.2f}\n"
        receipt += "=" * 40 + "\n"
        receipt += "Thank you for your purchase!\n"
        receipt += "=" * 40 + "\n"
        return receipt

    # Handle final checkout: update stock in DB, record transaction, clear cart
    def checkout(self, cart, username):
        conn = sqlite3.connect("vending_machine.db")
        cur = conn.cursor()

        for pid, item in cart.cart.items():
            cur.execute("UPDATE Products SET stock = stock - ? WHERE productID = ?", (item.stock, pid))

        conn.commit()
        conn.close()

        self.inventory = self.load_inventory()
        self.save_transactions(cart, username)
        cart.clear_cart()
        return "\nPurchase completed and saved!"

    # Update product stock (used as utility method)
    def update_stock(self, pid, qty):
        con = sqlite3.connect("vending_machine.db")
        cur = con.cursor()
        cur.execute("UPDATE Products SET stock = ? WHERE productID = ?", (qty, pid))
        con.commit()
        con.close()
        self.inventory = self.load_inventory()
        return "Stock updated successfully."

    # Save transactions from cart into CartTransactions table
    def save_transactions(self, cart, username):
        conn = sqlite3.connect("vending_machine.db")
        cur = conn.cursor()
        for item in cart.cart.values():
            cur.execute("""
                INSERT INTO CartTransactions (productID, quantity, totalPrice, username)
                VALUES (?, ?, ?, ?)
            """, (item.id, item.stock, item.price, username))
        conn.commit()
        conn.close()
        return "Transaction recorded."

    # Retrieve latest transaction history
    def get_transaction_history(self):
        conn = sqlite3.connect("vending_machine.db")
        cur = conn.cursor()
        cur.execute("""
            SELECT productID, quantity, totalPrice, transactionDate, username
            FROM CartTransactions
            ORDER BY transactionDate DESC
            LIMIT 20
        """)
        transactions = cur.fetchall()
        conn.close()

        if not transactions:
            return "No previous transactions found."

        output = "\nRecent Transactions:\n"
        output += f"{'ProductID':<10} {'Qty':<5} {'Total($)':<10} {'Date':<20} {'User'}\n"
        output += "-" * 55 + "\n"
        for row in transactions:
            pid, qty, total, date, username = row
            output += f"{pid:<10} {qty:<5} ${total:<9.2f} {date:<20} {username}\n"
        return output

    # Generate a sales chart (top 10 products) and return as base64 image
    def generate_sales_chart(self):
        conn = sqlite3.connect("vending_machine.db")
        cur = conn.cursor()
        cur.execute("""
            SELECT p.productName, SUM(t.quantity) as total_sold
            FROM CartTransactions t
            JOIN Products p ON p.productID = t.productID
            GROUP BY p.productID
            ORDER BY total_sold DESC LIMIT 10
        """)
        data = cur.fetchall()
        conn.close()

        if not data:
            return "No data to plot."

        names = [row[0] for row in data]
        values = [row[1] for row in data]

        fig, ax = plt.subplots(figsize=(10, 6))
        bars = ax.bar(range(len(names)), values, color='skyblue', alpha=0.7)
        ax.set_title("Top Selling Products", fontsize=14, fontweight='bold')
        ax.set_xlabel("Product", fontsize=12)
        ax.set_ylabel("Units Sold", fontsize=12)
        ax.set_xticks(range(len(names)))
        ax.set_xticklabels(names, rotation=45, ha='right')

        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{value}', ha='center', va='bottom', fontweight='bold')

        plt.tight_layout()

        buf = BytesIO()
        fig.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        plt.close(fig)

        img_data = base64.b64encode(buf.getvalue()).decode('utf-8')
        return img_data

# Handles user login authentication
class UserAuth:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.user = (username, password)

    def authentication(self):
        conn = sqlite3.connect("vending_machine.db")
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM Users WHERE username=? AND password=?", (self.username, self.password))
        return cur.fetchone() is not None
