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

    def run(self):
        buffer = ""
        while True:
            try:
                response = self.client.recv(self.BUFSIZE).decode("utf-8")
                buffer += response

                if "Enter" in buffer or "command" in buffer or "You:" in buffer:
                    print(f"Server:\n{buffer}")
                    buffer = ""
                    message = input("You: ")
                    self.client.send(message.encode("utf-8"))

                    if message.lower() == "exit":
                        print(self.client.recv(self.BUFSIZE).decode("utf-8"))
                        break


            except Exception as e:
                print(f"Error: {e}")
                break

        self.client.close()


if __name__ == "__main__":
    client = Client()
    client.run()
