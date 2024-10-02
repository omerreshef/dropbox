import unittest
import struct
from unittest.mock import MagicMock

from dropbox_system.common.request_handler import RequestHandler


class TestServerHandler(unittest.TestCase):
    def test_send_header(self):
        """
        Check the method send_header of RequestHandler.
        Call the funtion and verify socket.send is triggered with the required parameter.
        """
        mock_socket = MagicMock()
        handler = RequestHandler(mock_socket)
        header = b'HEADER'
        handler.send_header(header)
        mock_socket.send.assert_called_once_with(header)
    
    def test_receive_numeric_value(self):
        """
        Check the method receive_numeric_value of RequestHandler.
        Call the funtion and verify socket.recv is triggered and returned the right value.
        """
        mock_socket = MagicMock()
        handler = RequestHandler(mock_socket)
        mock_socket.recv.return_value = struct.pack('I', 1234)
        
        result = handler.receive_numeric_value()
        self.assertEqual(result, 1234)
        mock_socket.recv.assert_called_once_with(handler.NUMERIC_FIELD_SIZE)
    
    def test_socket_close_on_request_handler_del(self):
        """
        Check the __del__ function of RequestHandler.
        Call the funtion and verify the socket is closed.
        """
        mock_socket = MagicMock()
        handler = RequestHandler(mock_socket)
        del handler
        mock_socket.close.assert_called_once()
        
if __name__ == '__main__':
    unittest.main()
