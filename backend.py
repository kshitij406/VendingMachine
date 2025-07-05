import sqlite3

# Product class represents an individual product in the vending machine
class Product:
    def __init__(self, id, name, price, stock):
        self.id = id
        self.name = name
        self.price = price
        self.stock = stock

    # Decrease stock by quantity if available
    def update_stock(self, quantity):
        if self.stock >= quantity:
            self.stock -= quantity
            return True
        return False

    # String representation of a product
    def __str__(self):
        return f"Product: {self.name}, Price: ${self.price:.2f}, Stock: {self.stock}"

# Cart class manages cart operations
class Cart:
    def __init__(self):
        self.cart = {}  # Dictionary of productID -> Product object (used to track cart items)

    # Add product to cart
    def add_item(self, product_id, quantity, inventory):
        if product_id in inventory:
            product = inventory[product_id]
            if product.update_stock(quantity):
                if product_id not in self.cart:
                    # Store total price and quantity in a Product object for simplicity
                    self.cart[product_id] = Product(product_id, product.name, product.price * quantity, quantity)
                else:
                    existing = self.cart[product_id]
                    existing.stock += quantity
                    existing.price += product.price * quantity
                return f"{quantity} units of '{product.name}' added to cart."
            else:
                return "Not enough stock."
        else:
            return f"Product ID '{product_id}' does not exist."

    # View cart contents
    def view_items(self):
        if not self.cart:
            return "Cart is empty."
        output = "Cart:\n"
        output += f"{'ProductID':<10} {'Name':<20} {'Total':<10} {'Qty':<6}\n"
        output += "-" * 50 + "\n"
        for pid, product in self.cart.items():
            output += f"{pid:<10} {product.name:<20} ${product.price:<9.2f} {product.stock:<6}\n"
        return output

    # Calculate total cost of items in the cart
    def calculate_total(self):
        return sum(product.price for product in self.cart.values())

    # Clear all items from the cart
    def clear_cart(self):
        if self.cart:
            self.cart.clear()
            print("The cart was cleared.")
        else:
            print("The cart is already empty.")

# VendingMachine class handles inventory, checkout, and database operations
class VendingMachine:
    def __init__(self):
        self.inventory = self.load_inventory()  # Load inventory from database

    # Load inventory from the 'Products' table in the SQLite database
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

    # Display all available products
    def display_products(self):
        message = f"{'ProductID':<10} {'Name':<20} {'Price':<10} {'Stock':<6}\n"
        message += "-" * 50 + "\n"
        for pid, product in self.inventory.items():
            message += f"{pid:<10} {product.name:<20} ${product.price:<9.2f} {product.stock:<6}\n"
        return message

    # Generate a formatted receipt from the cart contents
    def generate_receipt(self, cart):
        receipt = "\n" + "=" * 40 + "\n"
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

    # Finalize purchase: update inventory, record transaction, and clear cart
    def checkout(self, cart):
        self.save_inventory()
        self.save_transactions(cart)
        cart.clear_cart()
        return "\nPurchase completed and saved!"

    # Save current inventory state to the database
    def save_inventory(self):
        conn = sqlite3.connect("vending_machine.db")
        cur = conn.cursor()
        for product in self.inventory.values():
            cur.execute("""
                INSERT OR REPLACE INTO Products (productID, productName, price, stock)
                VALUES (?, ?, ?, ?)
            """, (product.id, product.name, product.price, product.stock))
        conn.commit()
        conn.close()

    # Save cart transaction to the CartTransactions table
    def save_transactions(self, cart):
        conn = sqlite3.connect("vending_machine.db")
        cur = conn.cursor()
        for item in cart.cart.values():
            cur.execute("""
                INSERT INTO CartTransactions (productID, quantity, totalPrice)
                VALUES (?, ?, ?)
            """, (item.id, item.stock, item.price))
        conn.commit()
        conn.close()
        return "Transaction recorded."

    # Fetch transaction history from the database
    def get_transaction_history(self):
        conn = sqlite3.connect("vending_machine.db")
        cur = conn.cursor()
        cur.execute("""
            SELECT productID, quantity, totalPrice, transactionDate
            FROM CartTransactions
            ORDER BY transactionDate DESC
            LIMIT 20
        """)
        transactions = cur.fetchall()
        conn.close()

        if not transactions:
            return "No previous transactions found."

        output = "\nRecent Transactions:\n"
        output += f"{'ProductID':<10} {'Qty':<5} {'Total($)':<10} {'Date'}\n"
        output += "-" * 50 + "\n"
        for row in transactions:
            pid, qty, total, date = row
            output += f"{pid:<10} {qty:<5} ${total:<9.2f} {date}\n"
        return output

