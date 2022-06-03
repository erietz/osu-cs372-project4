import socket
from src.chat_socket import ChatSocket

SERVER_NAME = "localhost"
SERVER_PORT = 50000
SERVER_ADDRESS = (SERVER_NAME, SERVER_PORT)


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        # bind the socket to the address
        server.bind(SERVER_ADDRESS)

        # accept exactly one connection and refuse any more attempted
        # connections
        server.listen(0)
        print(f"Server listening on {SERVER_NAME}:{SERVER_PORT}")

        connection_socket, client_address = server.accept()
        print("connected by", client_address)

        with ChatSocket(connection_socket) as connection_socket:
            print("waiting for message")
            message = connection_socket.receive_message()
            print(message)
            print("type \\q to quit")

            print("Enter message to send...")
            send_and_receive_messages(connection_socket)

def send_and_receive_messages(sock: ChatSocket) -> None:
    while (msg := input("> ")) != "/q":
        sock.send_message(msg)
        print(sock.receive_message())


if __name__ == '__main__':
    main()
