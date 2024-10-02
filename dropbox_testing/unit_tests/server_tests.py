import unittest
from unittest.mock import patch, MagicMock
import argparse
from dropbox_system.server.server import Server, get_arguments_from_user

class TestServer(unittest.TestCase):

    @patch('socket.socket')
    def test_server_initialization(self, mock_socket):
        """
        Check the constructor of Server.
        Call the funtion and verify the socket is initialized as expected.
        """
        mock_socket_instance = MagicMock()
        mock_socket.return_value = mock_socket_instance

        server = Server('127.0.0.1', 9090)
        mock_socket_instance.bind.assert_called_with(('127.0.0.1', 9090))
        mock_socket_instance.listen.assert_called_once_with(60)

    @patch('socket.socket')
    @patch('threading.Thread')
    def test_server_start_and_accept_clients(self, mock_thread, mock_socket):
        """
        Check the method `start` of Server.
        Call the funtion and verify it is executed as expected.
        """
        mock_socket_instance = MagicMock()
        mock_socket.return_value = mock_socket_instance
        mock_client_socket = MagicMock()

        server = Server('127.0.0.1', 9090)
        
        mock_socket_instance.accept.side_effect = [(mock_client_socket, ('client_ip', 12345)), KeyboardInterrupt]

        # The server is starting and immediately stops, duo to KeyboardInterrupt
        server.start()

        mock_thread.assert_called_once_with(target=server.handle_client, args=(mock_client_socket,))
        mock_thread.return_value.start.assert_called_once()
        mock_socket_instance.close.assert_called_once()

    @patch('argparse.ArgumentParser.parse_args', return_value=argparse.Namespace(address='192.168.1.1', port=9090))
    def test_get_arguments_from_user(self, mock_parse_args):
        """
        Test the argument parser that executed on the __main__ function.
        """
        address, port = get_arguments_from_user()
        self.assertEqual(address, '192.168.1.1')
        self.assertEqual(port, 9090)
        print("Server correctly parses arguments.")

if __name__ == '__main__':
    unittest.main()
