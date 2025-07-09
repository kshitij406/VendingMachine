from socket import *

class Client:
    def __init__(self):
        self.HOST = "localhost"
        self.PORT = 5556
        self.ADDRESS = (self.HOST, self.PORT)
        self.BUFSIZE = 1024
        self.client = None

    def connect(self):
        self.client = socket(AF_INET, SOCK_STREAM)
        self.client.connect(self.ADDRESS)

    def send_command(self, command):
        if not self.client:
            raise ConnectionError("Client not connected")
        self.client.send(command.encode("utf-8"))
        return self.client.recv(self.BUFSIZE).decode("utf-8")
    
    def send_command_large(self, command):
        """Send command and receive large data (like chart images)"""
        if not self.client:
            raise ConnectionError("Client not connected")
        self.client.send(command.encode("utf-8"))
        response = self.client.recv(self.BUFSIZE).decode("utf-8")
        if response.startswith("CHART_SIZE:"):
            # Handle large chart data
            size = int(response.split(":")[1])
            self.client.send("READY".encode("utf-8"))  # Acknowledgment
            
            # Receive the chart data in chunks
            chart_data = b""
            while len(chart_data) < size:
                chunk = self.client.recv(min(self.BUFSIZE, size - len(chart_data)))
                if not chunk:
                    break
                chart_data += chunk
            return chart_data.decode("utf-8")
        else:
            return response
