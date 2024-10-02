import unittest
import struct
import socket
from unittest.mock import patch, MagicMock
from dropbox_system.client.client_handler import ClientHandler
from dropbox_system.common.xor_encryption import xor_data

class TestServerHandler(unittest.TestCase):
    def setUp(self):
        self.mock_socket = MagicMock(spec=socket.socket)
        self.client_handler = ClientHandler(self.mock_socket)

    def test_send_request_header(self):
        """
        Test the `_send_request_header` method of the `ClientHandler` class.
        """
        request_code = ClientHandler.REMOVE_FILE_REQUEST_CODE
        request = b"request"
        packed_header = struct.pack("II", request_code, len(request))

        with patch.object(self.client_handler, 'send_header') as mock_send_header:
            self.client_handler._send_request_header(request_code, request)

        mock_send_header.assert_called_once_with(packed_header)

    def test_parse_response_header(self):
        """
        Test the `_parse_response_header` method of the `ClientHandler` class.
        """
        response_type = ClientHandler.LOGIN_RESPONSE_CODE
        error_code = ClientHandler.SUCCESS
        response_len = 10

        with patch.object(self.client_handler, 'receive_numeric_value', side_effect=[response_type, error_code, response_len]):
            parsed_response = self.client_handler._parse_response_header()

        self.assertEqual(parsed_response, (response_type, error_code, response_len))
    
    def test_handle_quit_session_command(self):
        self.client_handler.QUIT_SESSION_REQUEST_CODE = 999
        request = b""
        packed_request = struct.pack("II", self.client_handler.QUIT_SESSION_REQUEST_CODE, len(request)) + request
        
        with patch.object(self.client_handler, 'send_header') as mock_send_header:
            self.client_handler.handle_quit_session_command()

        mock_send_header.assert_called_once_with(packed_request)

    @patch.object(ClientHandler, '_send_request_header')
    @patch.object(ClientHandler, 'send_data')
    @patch.object(ClientHandler, '_parse_response_header', return_value=(ClientHandler.REMOVE_FILE_REQUEST_CODE, ClientHandler.SUCCESS, 0))
    def test_handle_remove_file_command(self, mock_parse, mock_send_data, mock_send_header):
        """
        Test the `_handle_remove_file_command` method of the `ClientHandler` class.
        """
        file_name = "file.txt"
        request = struct.pack("I", len(file_name)) + file_name.encode()

        with patch('builtins.input', return_value=file_name):
            self.client_handler._handle_remove_file_command()

        mock_send_header.assert_called_once_with(self.client_handler.REMOVE_FILE_REQUEST_CODE, request)
        mock_send_data.assert_called_once_with(request)

    def test_are_passwords_equal(self):
        password = "PaVdsets13!"
        verify_password = password
        self.assertTrue(self.client_handler._are_passwords_equal(password, verify_password))

        verify_password = verify_password + "aaaa"
        self.assertFalse(self.client_handler._are_passwords_equal(password, verify_password))

if __name__ == '__main__':
    unittest.main()
