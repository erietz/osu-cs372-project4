from src.chat_socket import ChatSocket

SERVER_NAME = "localhost"
SERVER_PORT = 50000

with ChatSocket() as client:
    # client = ChatSocket()
    client.connect(SERVER_NAME, SERVER_PORT)

    print(f"connected to {SERVER_NAME}:{SERVER_PORT}")

    print("type /q to quit")
    print("Enter message to send...")

    while (msg := input("> ")) != "/q":
        client.send_message(msg)
        print(client.receive_message())


    # client.close()
