from socket import *
import threading
import traceback

from backend import VendingMachine
from backend import Cart

HOST = "localhost"
PORT = 5556
ADDRESS = (HOST, PORT)
BUFSIZE = 1024

server = socket(AF_INET, SOCK_STREAM)
server.bind(ADDRESS)
server.listen(5)


def handle_client(client_socket, client_address):
    print(f"[+] Connected to {client_address}")
    inventory = VendingMachine()
    inventory.load_inventory()
    cart = Cart()

    try:
        menu = f"""Hello {client_address}, welcome to the vending machine!

   FUNCTION                COMMAND
1. View All Products     -  [VIEW]
2. Add Products to Cart  -  [ADD]
3. View Cart             -  [CART]
4. Checkout              -  [CHECKOUT]
5. Exit                  -  [EXIT]
"""
        client_socket.send(menu.encode("utf-8"))
        client_socket.send("Enter your command: ".encode("utf-8"))

        while True:
            request = client_socket.recv(1024).decode().strip()
            if not request:
                print(f"[!] No command from {client_address}, skipping...")
                continue

            if request.startswith("VIEW"):
                message = inventory.display_products()
                client_socket.send(message.encode("utf-8"))
                client_socket.send("\nEnter next command: ".encode("utf-8"))

            elif request.startswith("ADD"):
                products = inventory.display_products()
                client_socket.send(products.encode("utf-8"))

                client_socket.send("Enter Product ID: ".encode("utf-8"))
                pid = client_socket.recv(1024).decode().strip()

                client_socket.send("Enter Quantity: ".encode("utf-8"))
                qty = int(client_socket.recv(1024).decode().strip())

                cart.add_item(pid, qty, inventory.inventory)
                client_socket.send("Item added to cart.".encode("utf-8"))
                client_socket.send("\nEnter next command: ".encode("utf-8"))

            elif request.startswith("CART"):
                cart_details = cart.view_items()
                client_socket.send(cart_details.encode("utf-8"))
                client_socket.send("\nEnter next command: ".encode("utf-8"))

            elif request.startswith("CHECKOUT"):
                receipt = inventory.checkout(cart)
                client_socket.send(receipt.encode("utf-8"))
                client_socket.send("\nEnter next command: ".encode("utf-8"))

            elif request.lower() == "exit":
                client_socket.send("Goodbye!".encode("utf-8"))
                break

            else:
                client_socket.send("Invalid command.".encode("utf-8"))
                client_socket.send("\nEnter next command: ".encode("utf-8"))


    except Exception as e:
        print(f"[!] Error with {client_address}: {e}")
        traceback.print_exc()

    finally:
        client_socket.close()
        print(f"[-] Disconnected from {client_address}")


# Main connection loop
while True:
    client, client_address = server.accept()
    thread = threading.Thread(target=handle_client, args=(client, client_address))
    thread.start()
    print(f"[=] Active Connections: {threading.active_count() - 1}")
