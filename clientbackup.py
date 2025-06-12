import pandas as pd

def load_inventory(file_path="inventory.txt"):
    items = []
    with open(file_path, "r") as file:
        products = file.read().strip().split("\n")
        for p in products:
            id, name, price, stock = p.split(", ")
            items.append({
                "id": id,
                "name": name,
                "price": float(price),
                "stock": int(stock)
            })
    return items

def display_products(inventory):
    print("\nAvailable Products:")
    for item in inventory:
        print(f"{item['id']} - {item['name']} - ${item['price']} - Stock: {item['stock']}")

def update_stock(inventory, product_id, quantity):
    for item in inventory:
        if item["id"] == product_id:
            if item["stock"] >= quantity:
                item["stock"] -= quantity
                return True
            return False
    return False

def add_to_cart(cart, inventory, product_id, quantity):
    for item in inventory:
        if item["id"] == product_id:
            if update_stock(inventory, product_id, quantity):
                if item["name"] in cart:
                    cart[item["name"]]["quantity"] += quantity
                    cart[item["name"]]["total_price"] += item["price"] * quantity
                else:
                    cart[item["name"]] = {
                        "quantity": quantity,
                        "total_price": item["price"] * quantity
                    }
                print("Item added to cart.")
            else:
                print("Not enough stock.")
            return
    print("Product ID not found.")

def view_cart(cart):
    if not cart:
        print("Cart is empty.")
        return
    print("\nCart Summary:")
    for name, data in cart.items():
        print(f"{name}: {data['quantity']} pcs - ${data['total_price']:.2f}")

def save_inventory(inventory, file_path="inventory.txt"):
    with open(file_path, "w") as file:
        for item in inventory:
            line = ", ".join([item["id"], item["name"], str(item["price"]), str(item["stock"])])
            file.write(line + "\n")

def save_transactions(cart, file_path="transactions.txt"):
    with open(file_path, "a") as file:
        for idx, (name, data) in enumerate(cart.items(), start=1):
            file.write(f"TRANSACTION {idx}: {name}, Quantity: {data['quantity']}, Total: ${data['total_price']:.2f}\n")

def checkout(cart, inventory):
    view_cart(cart)
    confirm = input("Do you want to confirm the purchase? (y/n): ")
    if confirm.lower() == 'y':
        save_inventory(inventory)
        save_transactions(cart)
        cart.clear()
        print("Purchase completed and saved!")

def main():
    inventory = load_inventory()
    cart = {}

    while True:
        print("""
1. View All Products 
2. Add Products to Cart   
3. View Cart 
4. Checkout   
        """)
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            display_products(inventory)
        elif choice == "2":
            display_products(inventory)
            product_id = input("Enter Product ID: ").strip()
            quantity = int(input("Enter Quantity: "))
            add_to_cart(cart, inventory, product_id, quantity)
        elif choice == "3":
            view_cart(cart)
        elif choice == "4":
            checkout(cart, inventory)
        else:
            print("Invalid choice.")

        cont = input("Do you want to continue? (y/n): ")
        if cont.lower() == 'n':
            break

main()
