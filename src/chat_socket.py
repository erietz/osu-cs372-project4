"""
Author      : Ethan Rietz
Date        : 2022-06-03
Description : Wrapper class over the low level socket module

References:
    https://docs.python.org/3/library/socket.html
    https://docs.python.org/3/howto/sockets.html
    https://realpython.com/python-with-statement/
"""

import socket


class BrokenSocketConnection(Exception):
    def __init__(self, message: str = "socket connection broken"):
        super().__init__(message)


class ChatSocket:
    def __init__(self, sock: socket.socket = None):
        self.max_recv_length = 2048     # 2 KiB
        if sock is None:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = sock

    def __enter__(self):
        """called by the with statement to enter the runtime context"""
        return self

    def __exit__(self, *args, **kwargs):
        """called when the execution leaves the with code block"""
        self.close()

    def connect(self, host: str, port: int):
        self.sock.connect((host, port))

    def close(self):
        self.sock.close()

    def _send_message_length(self, length: int):
        if self.sock.send(str(length).encode()) == 0:
            raise BrokenSocketConnection()

    def _receive_message_length(self) -> int:
        data = self.sock.recv(self.max_recv_length).decode()
        if data == "":
            raise BrokenSocketConnection("error reading from socket")
        return int(data)

    def send_message(self, msg: str) -> None:
        msg = msg.encode()
        message_length = len(msg)

        # TODO: put these two calls in a loop to ensure client and server are
        # on the same page about the message length
        self._send_message_length(message_length)
        ack = self._receive_message_length()
        assert ack == message_length

        total_sent = 0
        while total_sent < message_length:
            sent = self.sock.send(msg[total_sent:])
            if sent == 0:
                raise BrokenSocketConnection()
            total_sent += sent

    def receive_message(self) -> str:
        # TODO: put these two calls in a loop like in self.send_message()
        message_length = self._receive_message_length()
        self._send_message_length(message_length)

        chunks = []
        bytes_received = 0
        while bytes_received < message_length:
            remaining_length = message_length - bytes_received
            chunk = self.sock.recv(min(remaining_length, self.max_recv_length))
            if chunk == b'':
                raise BrokenSocketConnection()
            chunks.append(chunk)
            bytes_received += len(chunk)
        return b''.join(chunks).decode()

    def chat(self, input_prompt="> ") -> None:
        try:
            while (msg := input(input_prompt)) != "/q":
                self.send_message(msg)
                print(self.receive_message())
        except BrokenSocketConnection as ex:
            print(ex)
