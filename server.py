from socket import *
import threading
import traceback
import sqlite3
from backend import VendingMachine, Cart, UserAuth

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

        # Authentication
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
                    message = inventory.display_products()
                    client_socket.send(message.encode("utf-8"))

                elif request.lower().startswith("add"):
                    try:
                        _, pid, qty = request.split()
                        pid = int(pid)
                        qty = int(qty)
                        message = cart.add_item(pid, qty, inventory.inventory)
                        client_socket.send(message.encode("utf-8"))
                    except Exception:
                        client_socket.send("Invalid ADD format. Use: ADD <product_id> <quantity>\n".encode("utf-8"))

                elif request.lower().startswith("cart"):
                    cart_details = cart.view_items()
                    client_socket.send(cart_details.encode("utf-8"))

                elif request.lower().startswith("receipt"):
                    receipt = inventory.generate_receipt(cart)
                    client_socket.send(receipt.encode("utf-8"))

                elif request.lower().startswith("checkout"):
                    checkout = inventory.checkout(cart, username)
                    client_socket.send(checkout.encode('utf-8'))

                elif request.lower().startswith("history"):
                    history = inventory.get_transaction_history()
                    client_socket.send(history.encode('utf-8'))

                elif request.lower().startswith("chart"):
                    chart_data = inventory.generate_sales_chart()
                    if chart_data and chart_data != "No data to plot.":
                        chart_data_bytes = chart_data.encode("utf-8")
                        size = len(chart_data_bytes)
                        client_socket.send(f"CHART_SIZE:{size}".encode("utf-8"))
                        client_socket.recv(self.BUFSIZE)
                        client_socket.sendall(chart_data_bytes)
                    else:
                        client_socket.send("NO_CHART".encode("utf-8"))

                elif request.upper().startswith("CHANGE_STOCK"):
                    try:
                        _, pid, qty = request.split()
                        pid = int(pid)
                        qty = int(qty)
                        inventory.update_stock(pid, qty)
                        client_socket.send(f"Stock updated for Product ID {pid} to {qty}.".encode("utf-8"))
                    except Exception as e:
                        client_socket.send(
                            f"Error updating stock: {e}".encode("utf-8"))

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
            return
        except ConnectionAbortedError:
            print(f"[!] Connection aborted by client {client_address}.")
            return
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
