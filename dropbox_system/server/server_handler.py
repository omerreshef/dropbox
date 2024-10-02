import os
import struct
import shutil
import socket
import struct

import dropbox_system.server.request_parser
from dropbox_system.common.request_handler import RequestHandler
from dropbox_system.server.db_communicator import DataBaseCommunicator


class ServerHandler(RequestHandler):
    """
    This class is handling various of requests, sent by a client and waiting for a response.
    """

    def __init__(self, sock: socket.socket, files_directory_path: str) -> None:
        """
        Initiating the ServerHandler with a socket, database communicator, and files directory path.

        :param sock (socket.socket): The socket to handle communication.
        :param database_communicator (DataBaseCommunicator): The object for database operations with the users DB.
        :param files_directory_path (str): The path where user files are stored.
        """
        super(ServerHandler, self).__init__(sock)
        self.database_communicator = DataBaseCommunicator()
        self.logged_in_user = None
        self.files_directory_path = files_directory_path
        self._create_users_directory_if_not_exists()
        self.should_exit = False
        self.request_handlers = \
        {
            self.REGISTER_REQUEST_CODE: self._handle_register_request,
            self.LOGIN_REQUEST_CODE: self._handle_login_request,
            self.QUIT_SESSION_REQUEST_CODE: self._handle_quit_session_request,
            self.REMOVE_FILE_REQUEST_CODE: self._handle_remove_file_request,
            self.DOWNLOAD_FILE_REQUEST_CODE: self._handle_download_file_request,
            self.UPLOAD_FILE_REQUEST_CODE: self._handle_upload_file_request,
            self.LIST_FILES_REQUEST_CODE: self._handle_list_files_request,
            self.CREATE_DIRECTORY_REQUEST_CODE: self._handle_create_directory_request,
        }

    def start_handler(self) -> None:
        """
        Start handling incoming user commands in a loop until the server exits.
        """
        while not self.should_exit:
            request_id, message = self._parse_user_command()
            self.request_handlers[request_id](message)

    def _create_users_directory_if_not_exists(self) -> None:
        """
        Create a directory for user files if it does not already exist.
        """
        if not os.path.exists(self.files_directory_path):
            os.mkdir(self.files_directory_path)

    def _parse_user_command(self) -> tuple:
        """
        Parse the requested user command by analyzing the received socket data.

        Returns:
            tuple: A tuple containing the request ID and the message content.
        """
        request_id = self.receive_numeric_value()
        request_len = self.receive_numeric_value()
        message = self.receive_bytes(request_len)
        return request_id, message

        
    def _create_response_header(self, response_code: int, error_code: int, response: bytes = b'') -> bytes:
        """
        Pack a response header for a new message.

        :param response_code (int): The response code to be sent.
        :param error_code (int): The error code of the response.
        :param response (bytes): Additional response data.

        Returns:
            bytes: The packed response header.
        """
        return struct.pack("III", response_code, error_code, len(response))
    
    def _handle_register_request(self, request: bytes) -> None:
        """
        Handle a registration request.

        :param request (bytes): The request data containing registration information (username, password..).
        """
        username, password = dropbox_system.server.request_parser.parse_register_request(request)
        try:
            self.database_communicator.create_new_user(username, password)
            user_directory_path = os.path.join(self.files_directory_path, username)
            if not os.path.exists(user_directory_path):
                os.mkdir(user_directory_path)
            response_header = self._create_response_header(self.REGISTER_RESPONE_CODE, self.SUCCESS)
        except dropbox_system.server.db_communicator.UserAlreadyExistsException:
            response_header = self._create_response_header(self.REGISTER_RESPONE_CODE, self.USER_ALREADY_EXISTS)

        self.send_header(response_header)
        self.should_exit = True

    def _handle_login_request(self, request: bytes) -> None:
        """
        Handle a login request.

        :param request (bytes): The request data containing login information (username, password).
        """
        username, password = dropbox_system.server.request_parser.parse_login_request(request)
        if self.database_communicator.is_username_exists(username):
            if self.database_communicator.is_password_correct(username, password):
                response_header = self._create_response_header(self.LOGIN_RESPONSE_CODE, self.SUCCESS)
                self.logged_in_user = username
                self.user_directory_path = os.path.join(self.files_directory_path, self.logged_in_user)
                if not os.path.exists(self.user_directory_path):
                    os.mkdir(self.user_directory_path)

            else:
                response_header = self._create_response_header(self.LOGIN_RESPONSE_CODE, self.INCORRECT_PASSWORD)
                self.should_exit = True
        else:
            response_header = self._create_response_header(self.LOGIN_RESPONSE_CODE, self.USER_NOT_EXISTS)
            self.should_exit = True
        
        self.send_header(response_header)

    def _write_file_content(self, file_path: str, file_content: bytes) -> None:
        """
        Write the content of a file to the specified path.
        """
        with open(file_path, 'wb') as file:
            file.write(file_content)

    def _handle_upload_file_request(self, request: bytes) -> None:
        """
        Handle a request to upload a file.

        :param request (bytes): The request data containing relevant information for the upload operation.
        """
        file_len, file_name, requested_dir = dropbox_system.server.request_parser.parse_upload_request(request)
        requested_path = os.path.join(self.user_directory_path, requested_dir)
        file_path = os.path.join(requested_path, file_name)

        if self.logged_in_user is None:
            response_header = self._create_response_header(self.UPLOAD_FILE_RESPONSE_CODE, self.USER_NOT_LOGGED_IN)
            self.send_header(response_header)
            return
        
        if not os.path.exists(requested_path):
            response_header = self._create_response_header(self.UPLOAD_FILE_RESPONSE_CODE, self.DIRECTORY_NOT_EXISTS)
            self.send_header(response_header)
            return

        if os.path.exists(file_path):
            response_header = self._create_response_header(self.UPLOAD_FILE_RESPONSE_CODE, self.FILE_ALREADY_EXISTS)
            self.send_header(response_header)
            return
        
        response_header = self._create_response_header(self.UPLOAD_FILE_RESPONSE_CODE, self.START_UPLOADING_FILE)
        self.send_header(response_header)

        file_content = self.receive_bytes(file_len)
        self._write_file_content(file_path, file_content)
            
        response_header = self._create_response_header(self.UPLOAD_FILE_RESPONSE_CODE, self.SUCCESS)
        self.send_header(response_header)

    def _handle_create_directory_request(self, request: bytes) -> None:
        """
        Handle a request to create a directory in the user's environment.

        :param request (bytes): The request data containing relevant information for the creating operation.
        """
        directory_name = dropbox_system.server.request_parser.parse_create_directory_request(request)

        if self.logged_in_user is None:
            response_header = self._create_response_header(self.CREATE_DIRECTORY_RESPONSE_CODE, self.USER_NOT_LOGGED_IN)
            self.send_header(response_header)
            return

        full_path = os.path.join(self.user_directory_path, directory_name)
        if os.path.exists(full_path):
            response_header = self._create_response_header(self.CREATE_DIRECTORY_RESPONSE_CODE, self.DIRECTORY_ALREADY_EXISTS)
            self.send_header(response_header)
        else:
            os.makedirs(full_path)
            response_header = self._create_response_header(self.CREATE_DIRECTORY_RESPONSE_CODE, self.SUCCESS)
            self.send_header(response_header)
    
    def _handle_download_file_request(self, request: bytes) -> None:
        """
        Handle a request to download a file.

        :param request (bytes): The request data containing relevant information for the download operation.
        """
        file_name = dropbox_system.server.request_parser.parse_download_request(request)

        if self.logged_in_user is None:
            response_header = self._create_response_header(self.DOWNLOAD_FILE_RESPONSE_CODE, self.USER_NOT_LOGGED_IN)
            self.send_header(response_header)
            return

        file_path = os.path.join(self.user_directory_path, file_name)

        if not os.path.exists(file_path):
            response_header = self._create_response_header(self.DOWNLOAD_FILE_RESPONSE_CODE, self.FILE_NOT_EXISTS)
            self.send_header(response_header)
            return

        if os.path.isdir(file_path):
            response_header = self._create_response_header(self.DOWNLOAD_FILE_RESPONSE_CODE, self.GOT_DIRECTORY_AS_INPUT)
            self.send_header(response_header)
            return

        with open(file_path, "rb") as file:
            file_content = file.read()
        file_length = len(file_content)
        response = struct.pack("Q", file_length)
        response_header = self._create_response_header(self.DOWNLOAD_FILE_RESPONSE_CODE, self.SUCCESS, response)
        self.send_header(response_header)
        self.send_data(response)
        self.send_file_content(file_content, file_length)

    def _remove_file(self, file_path: str) -> None:
        """
        Remove a specified file from the user's directory on the server.

        :param file_path (str): The path of the file to remove.
        """
        file_path = os.path.join(self.user_directory_path, file_path)

        if not os.path.exists(file_path):
            response_header = self._create_response_header(self.REMOVE_FILE_RESPONSE_CODE, self.FILE_NOT_EXISTS)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)
            response_header = self._create_response_header(self.REMOVE_FILE_RESPONSE_CODE, self.SUCCESS)
        else:
            os.remove(file_path)
            response_header = self._create_response_header(self.REMOVE_FILE_RESPONSE_CODE, self.SUCCESS)

        self.send_header(response_header)

    def _handle_remove_file_request(self, request: bytes) -> None:
        """
        Handle a request to remove a file.

        :params request (bytes): The request data containing removal information.
        """
        if self.logged_in_user is None:
            response_header = self._create_response_header(self.REMOVE_FILE_RESPONSE_CODE, self.USER_NOT_LOGGED_IN)
            self.send_header(response_header)
            return
        
        file_name = dropbox_system.server.request_parser.parse_remove_file_request(request)

        self._remove_file(file_name)

    def _handle_quit_session_request(self, request: bytes) -> None:
        """
        Handle a request to quit the user session.
        
        :params request (bytes): The request data.
        """
        if self.logged_in_user is None:
            self.logged_in_user = None
        self.should_exit = True

    def _handle_list_files_request(self, request: bytes) -> None:
        """
        Handle a request to list files in the user's directory on the server.

        :params request (bytes): The request data.
        """
        if self.logged_in_user is None:
            response_data = self._create_response_header(self.LIST_FILES_RESPONSE_CODE, self.USER_NOT_LOGGED_IN)
            self.send_header(response_data)
            return
        
        all_items = []

        for root, dirs, files in os.walk(self.user_directory_path):
            for name in dirs + files:
                relative_path = os.path.relpath(os.path.join(root, name), self.user_directory_path)
                all_items.append(relative_path)

        dir_list = " , ".join(all_items)
        dir_list_len = len(dir_list)

        response = struct.pack("I", dir_list_len) + dir_list.encode()
        response_header = self._create_response_header(self.LIST_FILES_RESPONSE_CODE, self.SUCCESS, response)
        self.send_header(response_header)
        self.send_data(response)
