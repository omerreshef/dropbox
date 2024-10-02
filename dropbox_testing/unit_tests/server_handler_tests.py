import unittest
import os
import struct
import shutil
from unittest.mock import Mock, patch

from dropbox_system.server.server_handler import ServerHandler
from dropbox_system.server.server import Server
from dropbox_system.common.xor_encryption import xor_data

class TestServerHandler(unittest.TestCase):
    def setUp(self):
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        db_file_path = os.path.join(project_root, 'dropbox_system', 'server', 'clients.db')
        user_files_path = os.path.join(project_root, 'dropbox_system', 'server', 'user_files')
        
        # Remove the database file if it exists
        if os.path.exists(db_file_path):
            os.remove(db_file_path)
        
        if os.path.exists(user_files_path):
            for filename in os.listdir(user_files_path):
                file_path = os.path.join(user_files_path, filename)
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)  # Remove files or links
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)  # Remove subdirectories

    def test_handle_quit_session_request(self):
        """
        Check the method handle_quit_session_request of ServerHandler.
        Call the funtion and verify the session is closed (handler.should_exit == True)
        """
        mock_socket = Mock()
        files_directory_path = 'path'
        handler = ServerHandler(mock_socket, files_directory_path)
        assert not handler.should_exit
        
        request = b"aaa"
        handler._handle_quit_session_request(request)
        
        assert handler.should_exit

    def test_handle_register_request(self):
        """
        Check the method handle_register_request of ServerHandler.
        Call the funtion and verify the user is created on the remote DB.
        """
        mock_socket = Mock()
        files_directory_path = 'path'
        handler = ServerHandler(mock_socket, files_directory_path)
        username = b"user"
        password = b"pass"
        request = struct.pack("I", len(username)) + username + struct.pack("I", len(password)) + password

        handler._handle_register_request(request)

        assert handler.database_communicator.is_username_exists(username.decode())
        assert handler.should_exit

    def test_handle_login_request(self):
        """
        Check the method create_new_user of ServerHandler.
        Call the funtion and verify the logged_in_user variable is equal to the expected username.
        """
        mock_socket = Mock()
        files_directory_path = 'path'
        handler = ServerHandler(mock_socket, files_directory_path)
        username = b"user"
        password = b"pass"
        request = struct.pack("I", len(username)) + username + struct.pack("I", len(password)) + password

        # Create the required user before logging in
        handler.database_communicator.create_new_user(username.decode(), password.decode())
        handler._handle_login_request(request)

        assert handler.logged_in_user == username.decode()
        assert not handler.should_exit
    
    def test_handle_download_file_request_file_not_found(self):
        """
        Check the method handle_download_file_request of ServerHandler with a file that not exists on the server.
        Call the funtion and verify we got the expected response.
        """
        mock_socket = Mock()
        files_directory_path = 'path'
        handler = ServerHandler(mock_socket, files_directory_path)
        
        handler.logged_in_user = 'user'
        handler.user_directory_path = 'path'
        
        file_name = b"file"
        request = struct.pack("I", len(file_name)) + file_name
        with patch('os.path.exists', return_value=False):
            handler._handle_download_file_request(request)

        assert mock_socket.send.called
        response_header = mock_socket.send.call_args[0][0]
        assert struct.unpack("III", response_header) == (handler.DOWNLOAD_FILE_RESPONSE_CODE, handler.FILE_NOT_EXISTS, 0)
    
    def test_handle_list_files_request(self):
        """
        Check the method handle_list_files_request of ServerHandler.
        Call the funtion and verify we got the expected response with the expected files list.
        """
        mock_socket = Mock()
        files_directory_path = 'path'
        handler = ServerHandler(mock_socket, files_directory_path)
        
        handler.logged_in_user = 'user'
        handler.user_directory_path = 'path'
        
        request = b""
        file1_name = "a.txt"
        file2_name = "b.txt"
    
        with patch('os.walk', return_value=[(handler.user_directory_path, [], [file1_name, file2_name])]):
            handler._handle_list_files_request(request)

        assert mock_socket.send.called
        response = xor_data(mock_socket.send.call_args[0][0])
        assert file1_name.encode() in response and file2_name.encode() in response

    def test_handle_upload_file_request_success(self):
        """
        Check the method handle_upload_file_request of ServerHandler.
        Call the funtion and verify we got the expected response code.
        """
        mock_socket = Mock()
        files_directory_path = 'path'
        handler = ServerHandler(mock_socket, files_directory_path)
        
        handler.logged_in_user = 'user'
        handler.user_directory_path = 'path'
        
        file_len = 1
        file_name = b"file.txt"
        requested_file_path = b""
        request = struct.pack("QII", file_len, len(file_name), len(requested_file_path)) + file_name + requested_file_path

        handler.receive_bytes = Mock(return_value=b'\x00')
        handler._write_file_content = Mock(return_value=None)
        handler._handle_upload_file_request(request)
        
        assert mock_socket.send.called
        response_header = mock_socket.send.call_args[0][0]
        assert struct.unpack("III", response_header) == (handler.UPLOAD_FILE_RESPONSE_CODE, handler.SUCCESS, 0)

if __name__ == '__main__':
    unittest.main()
