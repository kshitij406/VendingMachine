from socket import *

class Client:
    def __init__(self):
        self.HOST = "localhost"
        self.PORT = 5556
        self.ADDRESS = (self.HOST, self.PORT)
        self.BUFSIZE = 1024
        self.initialize_client_socket()

    def initialize_client_socket(self):
        self.client = socket(AF_INET, SOCK_STREAM)
        self.client.connect(self.ADDRESS)

    def send_command(self, command):
        try:
            self.client.send(command.encode("utf-8"))
            response = self.client.recv(self.BUFSIZE).decode("utf-8")
            return response
        except Exception as e:
            return f"Error: {e}"