import threading
import traceback
from socket import AF_INET, SOCK_STREAM, socket

from backend import VendingMachine, Cart, UserAuth  # Custom modules

class Server:
    def __init__(self):
        self.HOST = "127.0.0.1"
        self.PORT = 5556
        self.ADDRESS = (self.HOST, self.PORT)
        self.BUFSIZE = 1024
        self.initialize_server_socket()

    # Initialize the server socket and start listening for connections
    def initialize_server_socket(self):
        try:
            self.server_socket = socket(AF_INET, SOCK_STREAM)
            self.server_socket.bind(self.ADDRESS)
            self.server_socket.listen(5)
            print(f"[*] Server listening on {self.HOST}:{self.PORT}")
        except Exception as e:
            print(f"[!] Server failed to start: {e}")
            exit()

    # Handles client communication after connection
    def handle_client(self, client_socket, client_address):
        print(f"[+] Connected to {client_address}")

        inventory = VendingMachine()
        inventory.load_inventory()
        cart = Cart()

        # Authentication
        username = client_socket.recv(self.BUFSIZE).decode().strip()
        password = client_socket.recv(self.BUFSIZE).decode().strip()
        login = UserAuth(username, password)
        user_flag = login.authentication()
        client_socket.send(str(user_flag).encode('utf-8'))

        # If authentication fails, allow client to exit gracefully
        if not user_flag:
            try:
                possible_exit = client_socket.recv(self.BUFSIZE).decode().strip()
                if possible_exit.lower() == "exit":
                    print(f"[-] Client {client_address} disconnected after failed login.")
                    client_socket.close()
                    return
            except Exception as e:
                print(f"[!] Error after failed login from {client_address}: {e}")
                client_socket.close()
                return

        try:
            while True:
                request = client_socket.recv(self.BUFSIZE).decode().strip()

                # View available products
                if request.lower().startswith("view"):
                    message = inventory.display_products()
                    client_socket.send(message.encode("utf-8"))

                # Add product to cart
                elif request.lower().startswith("add"):
                    try:
                        _, pid, qty = request.split()
                        pid = int(pid)
                        qty = int(qty)
                        message = cart.add_item(pid, qty, inventory.inventory)
                        client_socket.send(message.encode("utf-8"))
                    except Exception:
                        client_socket.send("Invalid ADD format. Use: ADD <product_id> <quantity>\n".encode("utf-8"))

                # Remove product from cart
                elif request.lower().startswith("remove"):
                    try:
                        _, pid, qty = request.split()
                        pid = int(pid)
                        qty = int(qty)
                        message = cart.remove_item(pid, qty, inventory.inventory)
                        client_socket.send(message.encode("utf-8"))
                    except Exception:
                        client_socket.send("Invalid REMOVE format. Use: REMOVE <product_id> <quantity>\n".encode("utf-8"))

                # View cart contents
                elif request.lower().startswith("cart"):
                    cart_details = cart.view_items()
                    client_socket.send(cart_details.encode("utf-8"))

                # Generate receipt
                elif request.lower().startswith("receipt"):
                    if cart.cart:
                        receipt = inventory.generate_receipt(cart)
                        client_socket.send(receipt.encode("utf-8"))
                    else:
                        client_socket.send("Empty".encode("utf-8"))

                # Checkout and finalize transaction
                elif request.lower().startswith("checkout"):
                    if cart.cart:
                        checkout = inventory.checkout(cart, username)
                        client_socket.send(checkout.encode('utf-8'))
                    else:
                        client_socket.send("The cart is empty. Cannot proceed with checkout.".encode("utf-8"))

                # View order history
                elif request.lower().startswith("history"):
                    history = inventory.get_transaction_history()
                    client_socket.send(history.encode('utf-8'))

                # Change product stock
                elif request.upper().startswith("CHANGE_STOCK"):
                    try:
                        _, pid, qty = request.split()
                        pid = int(pid)
                        qty = int(qty)
                        inventory.update_stock(pid, qty)
                        client_socket.send(f"Stock updated for Product ID {pid} to {qty}.".encode("utf-8"))
                    except Exception as e:
                        client_socket.send(f"Error updating stock: {e}".encode("utf-8"))

                # Disconnect the client
                elif request.lower() == "exit":
                    try:
                        client_socket.send("Goodbye!".encode("utf-8"))
                    except ConnectionResetError:
                        print(f"[!] Client {client_address} disconnected before goodbye message.")
                    break

                # Invalid or unsupported command
                else:
                    client_socket.send("Invalid command.".encode("utf-8"))

        except ConnectionResetError:
            print(f"[!] Client {client_address} disconnected unexpectedly.")
        except ConnectionAbortedError:
            print(f"[!] Connection aborted by client {client_address}.")
        except Exception as e:
            print(f"[!] Error with {client_address}: {e}")
            traceback.print_exc()
        finally:
            client_socket.close()
            print(f"[-] Disconnected from {client_address}")

    # Accept client connections and assign each to a separate thread
    def run(self):
        while True:
            client, client_address = self.server_socket.accept()
            print(f"[+] Server Online — Connection from {client_address}")
            thread = threading.Thread(target=self.handle_client, args=(client, client_address))
            thread.start()
            print(f"[=] Active Connections: {threading.active_count() - 1}")

# Start the server
if __name__ == "__main__":
    server = Server()
    server.run()
