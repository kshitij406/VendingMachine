import sqlite3

class Product:
    def __init__(self, id, name, price, stock):
        self.id = id
        self.name = name
        self.price = price
        self.stock = stock

    def update_stock(self, quantity):
        if self.stock >= quantity:
            self.stock -= quantity
            return True
        return False

    def __str__(self):
        return f"Product: {self.name}, Price: {self.price}, Available Stock: {self.stock}"

class Cart:
    def __init__(self):
        self.items = {}

    def add_item(self, product_id, quantity, inventory):
        if product_id in inventory:
            product = inventory[product_id]
            if product.update_stock(quantity):
                if product_id not in self.items:
                    self.items[product_id] = {
                        "ID": product.id,
                        "Name": product.name,
                        "Total Price": product.price * quantity,
                        "Quantity": quantity
                    }
                else:
                    self.items[product_id]["Quantity"] += quantity
                    self.items[product_id]["Total Price"] += product.price * quantity
                message = f"{quantity} units of '{product.name}' added to cart."
            else:
                message = "There isn't enough stock."
            return message
        message = f"The product ID '{product_id}' doesn't exist."
        return message

    def view_items(self):
        if not self.items:
            return "Cart is empty."
        cart_in_string = "CART:\n"
        for pid, details in self.items.items():
            cart_in_string += f"{pid}: {details['Name']} - {details['Quantity']} pcs - ${details['Total Price']:.2f}\n"
        return cart_in_string

    def calculate_total(self):
        return sum(item["Total Price"] for item in self.items.values())

    def clear_cart(self):
        if self.items:
            self.items.clear()
            print("The cart was cleared.")
        else:
            print("The cart is already empty.")

class VendingMachine:
    def __init__(self):
        self.inventory = self.load_inventory()

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

    def display_products(self):
        message = f"{'ProductID':<10} {'Name':<20} {'Price':<10} {'Stock':<6}\n"
        message += "-" * 50 + "\n"
        for pid, product in self.inventory.items():
            message += f"{pid:<10} {product.name:<20} ${product.price:<9.2f} {product.stock:<6}\n"
        return message

    def checkout(self, cart):
        total = cart.calculate_total()
        receipt = f"\nReceipt:\n{cart.view_items()}\nTotal: ${total:.2f}\n"
        self.save_inventory()
        self.save_transactions(cart)
        cart.clear_cart()
        receipt += "\nPurchase completed and saved!"
        return receipt

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

    def save_transactions(self, cart):
        conn = sqlite3.connect("vending_machine.db")
        cur = conn.cursor()
        for item in cart.items.values():
            cur.execute("""
                INSERT INTO CartTransactions (productID, quantity, totalPrice)
                VALUES (?, ?, ?)
            """, (item["ID"], item["Quantity"], item["Total Price"]))
        conn.commit()
        conn.close()
        return "Transaction recorded."

