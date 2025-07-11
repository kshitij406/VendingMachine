from socket import AF_INET, SOCK_STREAM, socket


class Client:
    """Client class to handle connection and communication with the server."""

    def __init__(self):
        self.HOST = "localhost"
        self.PORT = 5556
        self.ADDRESS = (self.HOST, self.PORT)
        self.BUFSIZE = 1024
        self.client = None

    def connect(self):
        """Establish connection to the server."""
        self.client = socket(AF_INET, SOCK_STREAM)
        self.client.connect(self.ADDRESS)

    def send_command(self, command):
        """
        Send a command string to the server and receive a simple response.

        Args:
            command (str): Command to send.
        Returns:
            str: Server's response.
        """
        if not self.client:
            raise ConnectionError("Client not connected")
        self.client.send(command.encode("utf-8"))
        return self.client.recv(self.BUFSIZE).decode("utf-8")

