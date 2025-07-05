from socket import *

class Client:
    def __init__(self):
        # Server connection details
        self.HOST = "localhost"          # Server IP address
        self.PORT = 5556                 # Server port
        self.ADDRESS = (self.HOST, self.PORT)
        self.BUFSIZE = 1024              # Max size of data to receive at once

        self.initialize_client_socket()  # Connect to the server

    def initialize_client_socket(self):
        # Create a socket and connect to the server
        self.client = socket(AF_INET, SOCK_STREAM)
        self.client.connect(self.ADDRESS)

    def send_command(self, command):
        try:
            # Send command to the server
            self.client.send(command.encode("utf-8"))

            # Receive response from server
            response = self.client.recv(self.BUFSIZE).decode("utf-8")
            return response

        except Exception as e:
            # Return error message if something goes wrong
            return f"Error: {e}"
