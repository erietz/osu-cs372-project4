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
    """
    Used to send messages over a socket to another instance of ChatSocket.
    """
    def __init__(self, sock: socket.socket = None):
        """
        If <sock> is not provided, a new TCP socket is created.
        """
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
        """Connects to the server at host:port"""
        self.sock.connect((host, port))

    def close(self):
        """
        Closes the socket. This method is automatically called if the class is
        instantiated using 'with' as a context manager.
        """
        self.sock.close()

    def _send_message_length(self, length: int):
        """
        Sends <length> over the socket. This must be called before
        self.send_message() as we are reusing the socket for further transfers.
        This informs the receiver of the size of next incoming message.
        """
        if self.sock.send(str(length).encode()) == 0:
            raise BrokenSocketConnection()

    def _receive_message_length(self) -> int:
        """
        Receives the length of the next message (in bytes) to receive from the
        sender using self.receive_message().
        """
        data = self.sock.recv(self.max_recv_length).decode()
        if data == "":
            raise BrokenSocketConnection("error reading from socket")
        return int(data)

    def send_message(self, msg: str) -> None:
        """
        Sends <msg> over the socket.

        NOTE: This method first sends the length of the message, then waits for
        acknowledgment from the receiver that it got the length. If the
        receiver does not call self.receive_message() we are blocked.
        """
        msg = msg.encode()
        message_length = len(msg)

        self._send_message_length(message_length)
        # block so that receiver processes length first before getting mashed
        # together with the message.
        ack = self._receive_message_length()
        assert ack == message_length

        total_sent = 0
        while total_sent < message_length:
            sent = self.sock.send(msg[total_sent:])
            if sent == 0:
                raise BrokenSocketConnection()
            total_sent += sent

    def receive_message(self) -> str:
        """
        Receives a message of arbitrary length over the socket.
        """
        message_length = self._receive_message_length()
        # sender is blocked until we send back the length
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

    def chat(self, input_prompt: str = "> ") -> None:
        """
        1. Prompts the user for a message to send
        2. Sends the message over the socket
        3. Waits to receive the response message over the socket
        4. Repeats at step 1 unless user enters /q

        :param input_prompt: The prompt the user sees where they enter their
        text on the terminal.
        """
        # if other side of socket quits using /q, the socket connection is
        # broken and it throws an error.
        try:
            while (msg := input(input_prompt)) != "/q":
                self.send_message(msg)
                print(self.receive_message())
            self.close()
        except Exception as ex:
            print(ex)
