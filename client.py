"""
Author      : Ethan Rietz
Date        : 2022-06-03
Description : Code for the client side of the chat.

    - Needs to be started after the server
    - Uses port 50000 if not specified
    - If desired, a different port can be supplied as the first argument. For
      example: `python3 client.py <PORT NUMBER>`
"""

import sys
from src.chat_socket import ChatSocket


SERVER_NAME = "localhost"
if len(sys.argv) > 1:
    SERVER_PORT = int(sys.argv[1])
else:
    SERVER_PORT = 50000


with ChatSocket() as client:
    client.connect(SERVER_NAME, SERVER_PORT)

    print(f"Connected to {SERVER_NAME}:{SERVER_PORT}")

    print("Type /q to quit")
    print("Enter message to send...")

    client.chat()
