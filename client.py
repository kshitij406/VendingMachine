from socket import *
HOST = "localhost"
PORT = 5556
ADDRESS = (HOST, PORT)
BUFSIZE = 1024

client = socket(AF_INET, SOCK_STREAM)
client.connect(ADDRESS)

buffer = ""
while True:
    try:
        response = client.recv(BUFSIZE).decode("utf-8")
        buffer += response

        if "Enter" in buffer or "command" in buffer or "You:" in buffer:
            print(f"Server:\n{buffer}")
            buffer = ""
            message = input("You: ")
            client.send(message.encode("utf-8"))

            if message.lower() == "exit":
                break

    except Exception as e:
        print(f"Error: {e}")
        break

client.close()
