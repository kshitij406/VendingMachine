from socket import *

class Product:
    def __init__ (self, id, name, price, stock):
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

    # CART = {ID : {NAME, PRICE, QUANTITY}}
    def add_item(self, product_id, quantity, inventory):
        if product_id in inventory:
            product = inventory[product_id]
            if product.update_stock(quantity):
                if product_id not in self.items:
                    self.items[product_id] = {
                        "ID" : product.id,
                        "Name": product.name,
                        "Total Price": product.price * quantity,
                        "Quantity": quantity
                    }
                else:
                    self.items[product_id]["Quantity"] += quantity
                    self.items[product_id]["Total Price"] += product.price * quantity
                print(f"{quantity} units of '{product.name}' added to cart.")
            else:
                print("There isn't enough stock.")
            return 
        print(f"The product ID '{product_id}' doesn't exist.")

    def view_items(self):
        cart_in_string = "CART:\n"
        if not self.items:
            return "Cart is empty."
        print("\nCart Summary:")
        for pid, details in self.items.items():
            name = details["Name"]
            total_price = details["Total Price"]
            qty = details["Quantity"]
            cart_in_string += f"{pid}: {name} - {qty} pcs - ${total_price:.2f}"

        return cart_in_string

    def calculate_total(self):
        total = 0
        for item in self.items.values():
            total += item["Total Price"]
        return total

    def clear_cart(self):
        if self.items:
            self.items.clear()
            print("The cart was cleared")
        else:
            print("The cart is already empty")
        

class VendingMachine:
    def __init__(self):
        self.inventory = {}
        
    def load_inventory(self, file_path="inventory.txt"):
        with open(file_path, "r") as file:
            for line in file:
                id, name, price, stock = line.strip().split(", ")
                self.inventory[id] = Product(id, name, float(price), int(stock))
        return self.inventory

    def display_products(self):
        items = []
        message = "Available Products:\n"
        for pid, details in self.inventory.items():
            name = details.name
            price = details.price
            qty = details.stock
            message += f"{pid}: {name} - {qty} pcs - ${price:.2f}\n"

        return message

    def checkout(self, cart):
        cart.view_items()
        print(f"Total: ${cart.calculate_total():.2f}")
        confirm = input("Do you want to confirm the purchase? (y/n): ")
        if confirm.lower() == 'y':
            self.save_inventory()
            self.save_transactions(cart)
            cart.clear_cart()
            print("Purchase completed and saved!")
            
    def save_inventory(self, file_path="inventory.txt"):
        with open(file_path, "w") as file:
            for product in self.inventory.values():
                line = ", ".join([product.id, product.name, str(product.price), str(product.stock)])
                file.write(line + "\n")

    def save_transactions(self, cart, file_path="transactions.txt"):
        with open(file_path, "a") as file:
            for i, item in enumerate(cart.items.values(), start=1):
                pid = item["ID"]
                name = item["Name"]
                price = item["Total Price"]
                qty = item["Quantity"]
                line = f"TRANSACTION {i}: {pid}, {name}, ${price}, Qty: {qty}\n"
                file.write(line)
            print("Transaction recorded.")


    

def main():
    machine = VendingMachine()
    machine.load_inventory()
    cart = Cart()

    while True:
        print("""
1. View All Products 
2. Add Products to Cart   
3. View Cart 
4. Checkout   
5. Exit
        """)
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            machine.display_products()
        elif choice == "2":
            machine.display_products()
            product_id = input("Enter Product ID: ").strip()
            quantity = int(input("Enter Quantity: "))
            cart.add_item(product_id, quantity, machine.inventory)
        elif choice == "3":
            cart.view_items()
        elif choice == "4":
            machine.checkout(cart)
        elif choice == "5":
            break
        else:
            print("Invalid choice.")

        cont = input("Enter 'n' to exit or press Enter to continue: ")
        if cont.lower() == 'n':
            break

