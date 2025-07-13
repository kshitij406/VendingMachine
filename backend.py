import sqlite3
import requests
from bs4 import BeautifulSoup
import re

# Represents a product with id, name, price, and available stock
class Product:
    def __init__(self, id, name, price, stock):
        self.id = id
        self.name = name
        self.price = price
        self.stock = stock

    def __str__(self):
        return f"Product: {self.name}, Price: ${self.price:.2f}, Stock: {self.stock}"

# Handles operations related to the shopping cart
class Cart:
    def __init__(self):
        # Cart items: key = productID, value = Product object holding quantity and unit price
        self.cart = {}

    # Add a product to the cart if stock is sufficient
    def add_item(self, product_id, quantity, inventory):
        if product_id in inventory:
            product = inventory[product_id]

            if product.stock >= quantity:
                product.stock -= quantity  # Decrement from inventory stock

                if product_id not in self.cart:
                    # Store new item in cart with unit price
                    self.cart[product_id] = Product(product_id, product.name, product.price, quantity)
                else:
                    # Update existing item in cart
                    existing = self.cart[product_id]
                    existing.stock += quantity  # stock = quantity in cart

                return f"{quantity} units of '{product.name}' added to cart."
            else:
                return "Not enough stock."
        else:
            return f"Product ID '{product_id}' does not exist."

    # Remove a quantity of item from cart, and restore it to inventory
    def remove_item(self, product_id, quantity, inventory):
        if product_id not in self.cart:
            return f"Product ID '{product_id}' is not in the cart."

        cart_item = self.cart[product_id]

        if quantity >= cart_item.stock:
            removed_quantity = cart_item.stock
            del self.cart[product_id]
        else:
            cart_item.stock -= quantity
            removed_quantity = quantity

        inventory[product_id].stock += removed_quantity  # Restore to inventory
        return f"{removed_quantity} units of '{inventory[product_id].name}' removed from cart."

    # Display the contents of the cart
    def view_items(self, rate=1.0, currency="USD"):
        if not self.cart:
            return "Cart is empty."
        output = f"Cart (Prices in {currency.upper()}):\n"
        output += f"{'ProductID':<10} {'Name':<30} {'Total':<10} {'Qty':<6}\n"
        output += "-" * 50 + "\n"
        for pid, product in self.cart.items():
            converted = product.price * product.stock * rate  # Total = unit price × quantity × exchange rate
            output += f"{pid:<10} {product.name:<30} {currency.upper()}{converted:<9.2f} {product.stock:<6}\n"
        return output

    # Calculate total price of items in cart (without currency conversion)
    def calculate_total(self):
        return sum(product.price * product.stock for product in self.cart.values())

    # Empty the cart
    def clear_cart(self):
        if self.cart:
            self.cart.clear()
            print("The cart was cleared.")
        else:
            print("The cart is already empty.")

# Manages inventory, transactions, and currency conversions
class VendingMachine:
    def __init__(self, currency="usd"):
        self.default_currency = "usd"
        self.target_currency = currency
        self.rate = self.get_currency_exchange()
        self.inventory = self.load_inventory()

    # Get exchange rate from USD to target currency
    def get_currency_exchange(self):
        if self.target_currency != "usd":
            url = f"https://exchangerate.guru/{self.default_currency}/{self.target_currency}"
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            article = soup.find("article", class_="conversion-essense")
            rate_paragraph = article.find("p").text.strip()
            match = re.search(r"=\s*([\d.]+)", rate_paragraph)
            if match:
                return float(match.group(1))
            print("Rate not found")
            return 1
        return 1

    # Load inventory from database into a dictionary of Product objects
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

    # Reload the latest inventory from database
    def refresh_inventory(self):
        self.inventory = self.load_inventory()

    # Display all available products with currency conversion applied
    def display_products(self, cart=None):
        # self.refresh_inventory()
        message = f"{'ProductID':<10} {'Name':<30} {'Price':<15} {'Stock':<6}\n"
        message += "-" * 70 + "\n"

        for pid, product in self.inventory.items():
            # Subtract reserved quantity if item exists in cart
            reserved_qty = 0
            if cart and pid in cart.cart:
                reserved_qty = cart.cart[pid].stock  # quantity reserved in cart
            effective_stock = product.stock - reserved_qty

            converted_price = product.price * self.rate
            message += f"{pid:<10} {product.name:<30} ({self.target_currency.upper()}) {converted_price:<9.2f} {max(effective_stock, 0):<6}\n"
        return message

    # Create a receipt string from the cart contents
    def generate_receipt(self, cart):
        receipt = "\n" + "=" * 80 + "\n"
        receipt += " " * 12 + "PURCHASE RECEIPT\n"
        receipt += "=" * 40 + "\n"
        receipt += f"{'ProductID':<10} {'Name':<15} {'Qty':<5} {'Total':<8}\n"
        receipt += "-" * 40 + "\n"
        for pid, product in cart.cart.items():
            converted_price = product.price * self.rate
            receipt += f"{pid:<10} {product.name:<15} {product.stock:<5} {self.target_currency.upper()}{converted_price:<7.2f}\n"
        receipt += "-" * 40 + "\n"
        total = cart.calculate_total() * self.rate
        receipt += f"{'TOTAL':>32} : {self.target_currency.upper()}{total:.2f}\n"
        receipt += "=" * 40 + "\n"
        receipt += "Thank you for your purchase!\n"
        receipt += "=" * 40 + "\n"
        return receipt

    # Finalize checkout: update inventory, save transaction, clear cart
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

    # Manually update product stock
    def update_stock(self, pid, qty):
        con = sqlite3.connect("vending_machine.db")
        cur = con.cursor()
        cur.execute("UPDATE Products SET stock = ? WHERE productID = ?", (qty, pid))
        con.commit()
        con.close()
        self.inventory = self.load_inventory()
        return "Stock updated successfully."

    # Save a record of the current cart transaction to the database
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

    # Retrieve and display recent transaction history
    def get_transaction_history(self):
        conn = sqlite3.connect("vending_machine.db")
        cur = conn.cursor()
        cur.execute("""
            SELECT productID, quantity, totalPrice, transactionDate, username
            FROM CartTransactions
            ORDER BY transactionDate DESC LIMIT 20
        """)
        transactions = cur.fetchall()
        conn.close()
        if not transactions:
            return "No previous transactions found."
        output = "\nRecent Transactions:\n"
        output += f"{'ProductID':<10} {'Qty':<5} {'Total':<10} {'Date':<20} {'User'}\n"
        output += "-" * 55 + "\n"
        for row in transactions:
            pid, qty, total, date, username = row
            converted = total * self.rate
            output += f"{pid:<10} {qty:<5} {self.target_currency.upper()}{converted:<9.2f} {date:<20} {username}\n"
        return output

# Handles user login authentication
class UserAuth:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.user = (username, password)

    # Check user credentials against Users table
    def authentication(self):
        conn = sqlite3.connect("vending_machine.db")
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM Users WHERE username=? AND password=?", (self.username, self.password))
        return cur.fetchone() is not None
