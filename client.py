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

    def send_command_large(self, command):
        """
        Send a command that expects large response data (e.g., base64-encoded chart).

        Args:
            command (str): Command to send.
        Returns:
            str: Full decoded response from server.
        """
        if not self.client:
            raise ConnectionError("Client not connected")

        self.client.send(command.encode("utf-8"))
        response = self.client.recv(self.BUFSIZE).decode("utf-8")

        if response.startswith("CHART_SIZE:"):
            # Parse expected byte size
            size = int(response.split(":")[1])
            self.client.send("READY".encode("utf-8"))  # Acknowledge readiness

            # Receive full chart data
            chart_data = b""
            while len(chart_data) < size:
                chunk = self.client.recv(min(self.BUFSIZE, size - len(chart_data)))
                if not chunk:
                    break
                chart_data += chunk
            return chart_data.decode("utf-8")
        else:
            return response
