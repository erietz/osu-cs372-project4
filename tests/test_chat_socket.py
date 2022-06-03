import unittest
import socket
import  multiprocessing as mp
from src.chat_socket import ChatSocket, BrokenSocketConnection


class ChatSocketTests(unittest.TestCase):
    def setUp(self):
        hostname = "localhost"
        port = 0
        address = (hostname, port)
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((hostname, port))
        self.server.listen(0)
        actual_port = self.server.getsockname()[1]

        self.client = ChatSocket()
        self.client.connect(hostname, actual_port)

        connection_socket, client_address = self.server.accept()
        self.server_connection = ChatSocket(connection_socket)

    def tearDown(self):
        self.client.close()
        self.server.close()
        self.server_connection.close()

    def test_send_and_receive_message_length(self):
        send_length = 1234
        self.client._send_message_length(send_length)
        recv_length = self.server_connection._receive_message_length()
        self.assertEqual(recv_length, send_length)

    def test_send_and_receive_message_length_empty_string(self):
        send_length = 0
        self.client._send_message_length(send_length)
        recv_length = self.server_connection._receive_message_length()
        self.assertEqual(recv_length, send_length)

    def test_send_and_receive_message(self):
        send_string = "this is a message from the client to the server"

        def send():
            self.client.send_message(send_string)

        def recv(q):
            q.put(self.server_connection.receive_message())

        queue = mp.Queue()
        p_send = mp.Process(target=send)
        p_recv = mp.Process(target=recv, args=(queue,))
        p_send.start()
        p_recv.start()

        recv_string = queue.get()   # block until we get item from queue
        p_send.join()               # block until send process terminates
        p_recv.join()               # block until recv process terminates

        self.assertEqual(send_string, recv_string)
