from socket import *
import threading
import traceback

from backend import VendingMachine
from backend import Cart


class Server:
    def __init__(self):
        self.HOST = "127.0.0.1"
        self.PORT = 5556
        self.ADDRESS = (self.HOST, self.PORT)
        self.BUFSIZE = 1024
        self.initialize_server_socket()

    def initialize_server_socket(self):
        try:
            self.server_socket = socket(AF_INET, SOCK_STREAM)
            self.server_socket.bind(self.ADDRESS)
            self.server_socket.listen(5)
            print(f"[*] Server listening on {self.HOST}:{self.PORT}")
        except Exception as e:
            print(f"[!] Server failed to start: {e}")
            exit()

    def handle_client(self, client_socket, client_address):
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
                request = client_socket.recv(self.BUFSIZE).decode().strip()
                if not request:
                    print(f"[!] No command from {client_address}, skipping...")
                    continue

                if request.lower().startswith("view"):
                    message = inventory.display_products()
                    client_socket.send(message.encode("utf-8"))
                    client_socket.send("\nEnter next command: ".encode("utf-8"))

                elif request.lower().startswith("add"):
                    client_socket.send(inventory.display_products().encode("utf-8"))

                    client_socket.send("Enter Product ID: ".encode("utf-8"))
                    pid = client_socket.recv(self.BUFSIZE).decode("utf-8").strip()
                    pid = int(pid)

                    client_socket.send("Enter Quantity: ".encode("utf-8"))
                    qty_data = client_socket.recv(self.BUFSIZE).decode("utf-8").strip()
                    qty = int(qty_data)

                    message = cart.add_item(pid, qty, inventory.inventory)
                    client_socket.send(message.encode("utf-8"))
                    client_socket.send("\nEnter next command: ".encode("utf-8"))

                elif request.lower().startswith("cart"):
                    cart_details = cart.view_items()
                    client_socket.send(cart_details.encode("utf-8"))
                    client_socket.send("\nEnter next command: ".encode("utf-8"))

                elif request.lower().startswith("checkout"):
                    receipt = inventory.checkout(cart)
                    client_socket.send(receipt.encode("utf-8"))
                    client_socket.send("\nEnter next command: ".encode("utf-8"))


                elif request.lower() == "exit":
                    try:
                        client_socket.send("Goodbye!".encode("utf-8"))
                    except ConnectionResetError:
                        print(f"[!] Client {client_address} disconnected before goodbye message.")
                    break


                else:
                    client_socket.send("Invalid command.\nEnter next command: ".encode("utf-8"))

        except Exception as e:
            print(f"[!] Error with {client_address}: {e}")
            traceback.print_exc()

        finally:
            client_socket.close()
            print(f"[-] Disconnected from {client_address}")

    def run(self):
        while True:
            client, client_address = self.server_socket.accept()
            print(f"[+] Server Online — Connection from {client_address}")
            thread = threading.Thread(target=self.handle_client, args=(client, client_address))
            thread.start()
            print(f"[=] Active Connections: {threading.active_count() - 1}")


if __name__ == "__main__":
    server = Server()
    server.run()
