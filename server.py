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

    # Set up the server socket and begin listening for clients
    def initialize_server_socket(self):
        try:
            self.server_socket = socket(AF_INET, SOCK_STREAM)
            self.server_socket.bind(self.ADDRESS)
            self.server_socket.listen(5)
            print(f"[*] Server listening on {self.HOST}:{self.PORT}")
        except Exception as e:
            print(f"[!] Server failed to start: {e}")
            exit()

    # Handle communication with a connected client
    def handle_client(self, client_socket, client_address):
        print(f"[+] Connected to {client_address}")
        inventory = VendingMachine()
        cart = Cart()

        # Handle login
        username = client_socket.recv(self.BUFSIZE).decode().strip()
        password = client_socket.recv(self.BUFSIZE).decode().strip()
        login = UserAuth(username, password)
        user_flag = login.authentication()
        client_socket.send(str(user_flag).encode('utf-8'))

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

                if request.lower().startswith("view"):
                    inventory.refresh_inventory()
                    message = inventory.display_products()
                    client_socket.send(message.encode("utf-8"))

                elif request.lower().startswith("add"):
                    inventory.refresh_inventory()
                    try:
                        _, pid, qty = request.split()
                        pid = int(pid)
                        qty = int(qty)
                        message = cart.add_item(pid, qty, inventory.inventory)
                        client_socket.send(message.encode("utf-8"))
                    except Exception as e:
                        print(f"[ADD] Failed: {e}")
                        client_socket.send("Invalid ADD format. Use: ADD <product_id> <quantity>\n".encode("utf-8"))

                elif request.lower().startswith("remove"):
                    try:
                        _, pid, qty = request.split()
                        pid = int(pid)
                        qty = int(qty)
                        message = cart.remove_item(pid, qty, inventory.inventory)
                        client_socket.send(message.encode("utf-8"))
                    except Exception:
                        client_socket.send("Invalid REMOVE format. Use: REMOVE <product_id> <quantity>\n".encode("utf-8"))

                elif request.lower().startswith("cart"):
                    cart_details = cart.view_items(rate=inventory.rate, currency=inventory.target_currency)
                    client_socket.send(cart_details.encode("utf-8"))

                elif request.lower().startswith("receipt"):
                    if cart.cart:
                        receipt = inventory.generate_receipt(cart)
                        client_socket.send(receipt.encode("utf-8"))
                    else:
                        client_socket.send("Empty".encode("utf-8"))

                elif request.lower().startswith("checkout"):
                    if cart.cart:
                        checkout = inventory.checkout(cart, username)
                        client_socket.send(checkout.encode('utf-8'))
                    else:
                        client_socket.send("The cart is empty. Cannot proceed with checkout.".encode("utf-8"))

                elif request.lower().startswith("history"):
                    history = inventory.get_transaction_history()
                    client_socket.send(history.encode('utf-8'))

                elif request.upper().startswith("CHANGE_STOCK"):
                    try:
                        _, pid, qty = request.split()
                        pid = int(pid)
                        qty = int(qty)
                        inventory.update_stock(pid, qty)
                        client_socket.send(f"Stock updated for Product ID {pid} to {qty}.".encode("utf-8"))
                    except Exception as e:
                        client_socket.send(f"Error updating stock: {e}".encode("utf-8"))

                elif request.lower().startswith("currency"):
                    try:
                        _, new_currency = request.split()
                        inventory.target_currency = new_currency.lower()
                        inventory.rate = inventory.get_currency_exchange()
                        client_socket.send(f"Currency changed to {new_currency.upper()}.".encode("utf-8"))
                    except Exception as e:
                        print(f"[!] Currency change error: {e}")
                        client_socket.send("Failed to change currency.".encode("utf-8"))

                elif request.lower() == "exit":
                    try:
                        client_socket.send("Goodbye!".encode("utf-8"))
                    except ConnectionResetError:
                        print(f"[!] Client {client_address} disconnected before goodbye message.")
                    break

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

    # Accept and handle new client connections using threads
    def run(self):
        while True:
            client, client_address = self.server_socket.accept()
            print(f"[+] Server Online — Connection from {client_address}")
            thread = threading.Thread(target=self.handle_client, args=(client, client_address))
            thread.start()
            print(f"[=] Active Connections: {threading.active_count() - 1}")

# Entry point for server
if __name__ == "__main__":
    server = Server()
    server.run()
