import unittest
from unittest.mock import patch, MagicMock
import socket
import argparse
from dropbox_system.client.client import Client, get_arguments_from_user
from dropbox_system.client.client_handler import ClientHandler

class TestClient(unittest.TestCase):

    @patch('socket.socket')
    def test_client_connection_success(self, mock_socket):
        """
        Test the constructor of the `Client` class.
        Verify the connection is initiated and we got the expected result.
        """
        mock_socket_instance = MagicMock()
        mock_socket.return_value = mock_socket_instance

        client = Client('127.0.0.1', 8080)
        self.assertTrue(client.connected)
        mock_socket_instance.connect.assert_called_with(('127.0.0.1', 8080))

    @patch('socket.socket')
    def test_client_connection_failure(self, mock_socket):
        """
        Test the constructor of the `Client` class.
        Trigger socket error and verify we got the expected result.
        """
        mock_socket_instance = MagicMock()
        mock_socket_instance.connect.side_effect = socket.error("Connection failed")
        mock_socket.return_value = mock_socket_instance

        client = Client('127.0.0.1', 8080)
        self.assertFalse(client.connected)
        mock_socket_instance.connect.assert_called_with(('127.0.0.1', 8080))

    @patch('builtins.input', return_value=Client.REGISTER_CODE)
    @patch.object(ClientHandler, 'send_register_request')
    @patch('socket.socket')
    def test_handle_register_request(self, mock_socket, mock_send_register_request, mock_input):
        """
        Test the `handle_user_initial_request` method of the `Client` class.
        Enter input for register request and verify the register method is called.
        """
        mock_socket_instance = MagicMock()
        mock_socket.return_value = mock_socket_instance
        client = Client()
        client.handle_user_initial_request()

        mock_send_register_request.assert_called_once()
        mock_input.assert_called_with(client.INITIAL_REQUEST_EXPLAINATION)

    @patch('builtins.input', return_value=Client.LOGIN_CODE)
    @patch.object(ClientHandler, 'send_login_request')
    @patch('socket.socket')
    def test_handle_login_request(self, mock_socket, mock_send_login_request, mock_input):
        """
        Test the `handle_user_initial_request` method of the `Client` class.
        Enter input for login request and verify the login method is called.
        """
        mock_socket_instance = MagicMock()
        mock_socket.return_value = mock_socket_instance
        client = Client()
        client.handle_user_initial_request()

        mock_send_login_request.assert_called_once()
        mock_input.assert_called_with(client.INITIAL_REQUEST_EXPLAINATION)

    @patch('builtins.input', return_value='invalid request')
    @patch.object(ClientHandler, 'handle_quit_session_command')
    @patch('socket.socket')
    def test_handle_invalid_request(self, mock_socket, mock_handle_quit_session, mock_input):
        """
        Test the `handle_user_initial_request` method of the `Client` class.
        Enter invalid input for the initial request and verify the quit session method is called.
        """
        mock_socket_instance = MagicMock()
        mock_socket.return_value = mock_socket_instance
        client = Client()
        client.handle_user_initial_request()

        mock_handle_quit_session.assert_called_once()
        mock_input.assert_called_with(client.INITIAL_REQUEST_EXPLAINATION)

    @patch('argparse.ArgumentParser.parse_args', return_value=argparse.Namespace(address='192.168.1.1', port=9090))
    def test_get_arguments_from_user(self, mock_parse_args):
        """
        Test the argument parser that executed on the __main__ function.
        """
        address, port = get_arguments_from_user()
        self.assertEqual(address, '192.168.1.1')
        self.assertEqual(port, 9090)

if __name__ == '__main__':
    unittest.main()
