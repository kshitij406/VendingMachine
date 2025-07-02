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
            silent_counter = 0
            while True:
                request = client_socket.recv(self.BUFSIZE).decode().strip()
                silent_counter += 1
                if silent_counter % 50 == 0:
                    print(f"[i] Still connected to {client_address}, no new command.")

                if request.lower().startswith("view"):
                    message = inventory.display_products()
                    client_socket.send(message.encode("utf-8"))

                elif request.lower().startswith("add"):
                    try:
                        _, pid, qty = request.split()
                        pid = int(pid)
                        qty = int(qty)
                        message = cart.add_item(pid, qty, inventory.inventory)
                        client_socket.send(message.encode("utf-8"))
                    except Exception as e:
                        client_socket.send(f"Invalid ADD format. Use: ADD <product_id> <quantity>\n".encode("utf-8"))

                elif request.lower().startswith("cart"):
                    cart_details = cart.view_items()
                    client_socket.send(cart_details.encode("utf-8"))

                elif request.lower().startswith("checkout"):
                    receipt = inventory.checkout(cart)
                    client_socket.send(receipt.encode("utf-8"))

                elif request.lower() == "exit":
                    try:
                        client_socket.send("Goodbye!".encode("utf-8"))
                    except ConnectionResetError:
                        print(f"[!] Client {client_address} disconnected before goodbye message.")
                    break

                else:
                    client_socket.send("Invalid command.".encode("utf-8"))

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
