from socket import *
import threading
import traceback

from backend import VendingMachine
from backend import Cart

class Server:
    def __init__(self):
        # Server configuration
        self.HOST = "127.0.0.1"          # Localhost
        self.PORT = 5556                 # Port number for client connections
        self.ADDRESS = (self.HOST, self.PORT)
        self.BUFSIZE = 1024              # Max bytes per message
        self.initialize_server_socket()  # Start server socket setup

    def initialize_server_socket(self):
        try:
            # Create socket and bind to the address
            self.server_socket = socket(AF_INET, SOCK_STREAM)
            self.server_socket.bind(self.ADDRESS)
            self.server_socket.listen(5)  # Allow up to 5 queued connections
            print(f"[*] Server listening on {self.HOST}:{self.PORT}")
        except Exception as e:
            print(f"[!] Server failed to start: {e}")
            exit()

    def handle_client(self, client_socket, client_address):
        print(f"[+] Connected to {client_address}")

        # Initialize a VendingMachine and Cart instance for this client
        inventory = VendingMachine()
        inventory.load_inventory()
        cart = Cart()

        try:
            silent_counter = 0  # For optional idle monitoring/logging

            while True:
                # Wait for request from client
                request = client_socket.recv(self.BUFSIZE).decode().strip()
                silent_counter += 1

                # Optional: log if client is idle for many iterations
                if silent_counter % 50 == 0:
                    print(f"[i] Still connected to {client_address}, no new command.")

                # ── Handle client commands ──

                # VIEW: Display product inventory
                if request.lower().startswith("view"):
                    message = inventory.display_products()
                    client_socket.send(message.encode("utf-8"))

                # ADD <product_id> <quantity>: Add product to cart
                elif request.lower().startswith("add"):
                    try:
                        _, pid, qty = request.split()
                        pid = int(pid)
                        qty = int(qty)
                        message = cart.add_item(pid, qty, inventory.inventory)
                        client_socket.send(message.encode("utf-8"))
                    except Exception as e:
                        client_socket.send("Invalid ADD format. Use: ADD <product_id> <quantity>\n".encode("utf-8"))

                # CART: View items in the cart
                elif request.lower().startswith("cart"):
                    cart_details = cart.view_items()
                    client_socket.send(cart_details.encode("utf-8"))

                # RECEIPT: Generate formatted receipt
                elif request.lower().startswith("receipt"):
                    receipt = inventory.generate_receipt(cart)
                    client_socket.send(receipt.encode("utf-8"))

                # CHECKOUT: Save inventory/transaction, clear cart
                elif request.lower().startswith("checkout"):
                    checkout = inventory.checkout(cart)
                    client_socket.send(checkout.encode("utf-8"))

                # HISTORY: Return last 20 transactions
                elif request.lower().startswith("history"):
                    history = inventory.get_transaction_history()
                    client_socket.send(history.encode("utf-8"))

                # EXIT: Disconnect client gracefully
                elif request.lower() == "exit":
                    try:
                        client_socket.send("Goodbye!".encode("utf-8"))
                    except ConnectionResetError:
                        print(f"[!] Client {client_address} disconnected before goodbye message.")
                    break

                # Unknown command
                else:
                    client_socket.send("Invalid command.".encode("utf-8"))

        except Exception as e:
            print(f"[!] Error with {client_address}: {e}")
            traceback.print_exc()

        finally:
            # Always close client socket when done
            client_socket.close()
            print(f"[-] Disconnected from {client_address}")

    def run(self):
        # Accept incoming connections continuously
        while True:
            client, client_address = self.server_socket.accept()
            print(f"[+] Server Online — Connection from {client_address}")

            # Start a new thread to handle this client
            thread = threading.Thread(target=self.handle_client, args=(client, client_address))
            thread.start()

            # Show number of active client threads (excluding main thread)
            print(f"[=] Active Connections: {threading.active_count() - 1}")

# ─── Run the Server ───────────────────────────────────────────────────────
if __name__ == "__main__":
    server = Server()
    server.run()
