"""
Author      : Ethan Rietz
Date        : 2022-06-03
Description : Code for server side of the chat.

    - Needs to be started before the client
    - Uses port 50000 if not specified
    - If desired, a different port can be supplied as the first argument. For
      example: `python3 server.py <PORT NUMBER>`
"""

import socket
import sys
from src.chat_socket import ChatSocket


SERVER_NAME = "localhost"
if len(sys.argv) > 1:
    SERVER_PORT = sys.argv[1]
else:
    SERVER_PORT = 50000
SERVER_ADDRESS = (SERVER_NAME, SERVER_PORT)


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
    # bind the socket to the address
    server.bind(SERVER_ADDRESS)

    # listen for exactly one connection and refuse any more attempted
    # connections
    server.listen(0)
    print(f"Server listening for a connection on {SERVER_ADDRESS}")

    # accept a connection from a client
    connection_socket, client_address = server.accept()
    print("connected by", client_address)

    with ChatSocket(connection_socket) as connection_socket:
        print("waiting for message")
        message = connection_socket.receive_message()
        print(message)
        print("type /q to quit")
        print("Enter message to send...")
        connection_socket.chat()
