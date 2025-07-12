from socket import AF_INET, SOCK_STREAM, socket

class Client:
    # Handles connection and communication with the server
    def __init__(self):
        self.HOST = "localhost"         # Server address
        self.PORT = 5556                # Server port
        self.ADDRESS = (self.HOST, self.PORT)
        self.BUFSIZE = 1024             # Max size for each message chunk
        self.client = None              # Socket connection object

    def connect(self):
        # Establish connection to the server
        self.client = socket(AF_INET, SOCK_STREAM)
        self.client.connect(self.ADDRESS)

    def send_command(self, command):
        # Sends a command to the server and receives the full response
        if not self.client:
            raise ConnectionError("Client not connected")

        self.client.send(command.encode("utf-8"))

        data = b""
        while True:
            part = self.client.recv(self.BUFSIZE)
            data += part
            if len(part) < self.BUFSIZE:
                break

        return data.decode("utf-8")
