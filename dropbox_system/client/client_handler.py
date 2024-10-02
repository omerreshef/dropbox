import socket
import struct
import getpass
import os
import re

from dropbox_system.common.request_handler import RequestHandler

class ClientHandler(RequestHandler):
    """
    This class is handling client-side operations such as uploading, downloading, removing, 
    listing files, and managing user authentication.
    """
    ERROR_CODE_FIELD_SIZE = 4
    CREATE_DIRECTORY_COMMAND = "C"
    REMOVE_FILE_COMMAND = "R"
    UPLOAD_FILE_COMMAND = "U"
    DOWNLOAD_FILE_COMMAND = "D"
    QUIT_SESSION_COMMAND = "Q"
    LIST_FILES_COMMAND = "L"
    MINIMAL_USERNAME_LENGTH = 8
    MINIMAL_PASSWORD_LENGTH = 8

    def __init__(self, sock: socket.socket) -> None:
        """
        Initializes the ClientHandler object with a socket (to communicate the server) 
        and a command handler map - mapping between user input and required handling function.
        
        :param sock (socket.socket): The socket connected to the server.
        """
        super(ClientHandler, self).__init__(sock)
        self.command_handlers = \
        {
            self.REMOVE_FILE_COMMAND: self._handle_remove_file_command,
            self.UPLOAD_FILE_COMMAND: self._handle_upload_file_command,
            self.DOWNLOAD_FILE_COMMAND: self._handle_download_file_command,
            self.QUIT_SESSION_COMMAND: self.handle_quit_session_command,
            self.LIST_FILES_COMMAND: self._handle_list_files_command,
            self.CREATE_DIRECTORY_COMMAND: self._handle_create_directory_command,
        }

    def send_register_request(self) -> None:
        """
        Getting username and password input from the client, and sending registeration request with the given credentials.
        """
        username = input("choose username -> ")
        password = getpass.getpass("choose password -> ")
        verify_password = getpass.getpass("enter password again -> ")

        if not self._are_passwords_equal(password, verify_password):
            # Preform session quit with the server
            self.handle_quit_session_command()
            return
        
        if not self._are_credentials_strong_enough(username, password):
            # Preform session quit with the server
            self.handle_quit_session_command()
            return

        request = struct.pack("I", len(username)) + username.encode() + struct.pack("I", len(password)) + password.encode()

        print("Sending register request")
        self._send_request_header(self.REGISTER_REQUEST_CODE, request)
        self.send_data(request)

        response_type, error_code, _ = self._parse_response_header()
        if not self._is_correct_response_type(response_type, self.REGISTER_RESPONE_CODE):
            return
        
        if error_code == self.USER_ALREADY_EXISTS:
            print("User already exists! Try to choose different username.")
        if error_code == self.SUCCESS:
            print("Registered successfully!")

    def send_login_request(self) -> None:
        """
        Sends a login request to the server.
        It handles the server's response, which can indicate success or errors like a non-existent user 
        or an incorrect password.
        Upon successful login, the session starts.
        """
        request = self._create_login_request()
        self._send_request_header(self.LOGIN_REQUEST_CODE, request)
        self.send_data(request)

        response_type, error_code, _ = self._parse_response_header()

        if not self._is_correct_response_type(response_type, self.LOGIN_RESPONSE_CODE):
            return
        
        if error_code == self.USER_NOT_EXISTS:
            print("Username not exists! exiting")

        if error_code == self.INCORRECT_PASSWORD:
            print("Incorrect password! exiting")

        if error_code == self.SUCCESS:
            print("Logged in successfully!")
            self._start_session()
    
    def _send_request_header(self, request_code: int, request: bytes = b'') -> None:
        """
        Sends a request header to the server with the given request code and request payload.

        :param request_code (int): The request code to send.
        :param request (bytes): The request payload (default is an empty byte string).
        """
        request_header = struct.pack("II", request_code, len(request))
        self.send_header(request_header)

    def _parse_response_header(self) -> tuple:
        """
        Parses the response header received from the server. Extracts the response type,
        error code, and response length.

        Returns:
            tuple: A tuple containing response_type (int), error_code (int), and response_len (int).
        """
        response_type = self.receive_numeric_value()
        error_code = self.receive_numeric_value()
        response_len = self.receive_numeric_value()
        return response_type, error_code, response_len

    def _is_correct_response_type(self, response_type: int, expected_response_type: int) -> bool:
        """
        Checks if the responses type arguemts are equal.
        If not, return False and print a warning.
        """
        if response_type != expected_response_type:
            print("Got invalid response from the server.")
            return False
        return True
        
    def _are_passwords_equal(self, password: str, verify_password: str) -> bool:
        """
        Checks if the password arguemts are equal.
        If not, return False and print a warning.
        """
        if password != verify_password:
            print("Passwords are not equal, try again please")
            return False
        return True

    def _are_credentials_strong_enough(self, username: str, password: str) -> bool:
        """
        Validates the strength of the username and password by checking length and complexity.

        :param username (str): username to check.
        :param password (str): password to check.

        Returns:
            bool: True if the credentials meet the required standards, False otherwise.
        """
        are_credentials_strong_enough = True

        if len(username) < self.MINIMAL_USERNAME_LENGTH:
            print(f"Required username length - at least {self.MINIMAL_USERNAME_LENGTH} letters.")
            are_credentials_strong_enough = False
        
        if len(password) < self.MINIMAL_PASSWORD_LENGTH:
            print(f"Required password length - at least {self.MINIMAL_PASSWORD_LENGTH} letters.")
            are_credentials_strong_enough = False
        
        if re.search('[0-9]',password) is None:
            print("One digit is required in your password.")
            are_credentials_strong_enough = False

        if re.search('[A-Z]',password) is None:
            print("One capital is required in your password.")
            are_credentials_strong_enough = False

        if not are_credentials_strong_enough:
            print("Please try again.")

        return are_credentials_strong_enough

    def _create_remove_file_request(self) -> bytes:
        """
        Creates the request to remove a file by getting the file name as input.

        Returns:
            bytes: The packed request containing the file name.
        """
        file_name = input("Enter file name / directory name to remove. If you choose to remove a directory, all its files will be removed -> ")
        file_name_len = len(file_name)
        request = struct.pack("I", file_name_len) + file_name.encode()
        return request

    def _handle_remove_file_command(self) -> None:
        """
        Handles the file/directory removal operation by sending the appropriate request to the server
        and processing the server's response.
        """
        request = self._create_remove_file_request()
    
        print("sending request")
        self._send_request_header(self.REMOVE_FILE_REQUEST_CODE, request)
        self.send_data(request)

        response_type, error_code, _ = self._parse_response_header()
        if not self._is_correct_response_type(response_type, self.REMOVE_FILE_RESPONSE_CODE):
            return

        if error_code == self.FILE_NOT_EXISTS:
            print("File not exists! aborting.")
            return

        if error_code == self.SUCCESS:
            print("Removed successfully!")

    def _parse_download_file_response(self, response: bytes) -> int:
        """
        Parses the download file response.

        :param response (bytes): The server's response containing the file information.

        Returns:
            int: The length of the file to be downloaded.
        """
        file_len = struct.unpack("Q", response[:self.FILE_LEN_FIELD_SIZE])[0]
        return file_len

    def _handle_download_file_command(self) -> None:
        """
        Handles the file download operation, receiving the file from the server and saving it
        to a the requested directory.
        """
        file_name = input("Enter the file name to download -> ")
        file_name_len = len(file_name)

        request = struct.pack("I", file_name_len) + file_name.encode()
        print("sending request")
        self._send_request_header(self.DOWNLOAD_FILE_REQUEST_CODE, request)
        self.send_data(request)

        response_type, error_code, response_len = self._parse_response_header()


        if not self._is_correct_response_type(response_type, self.DOWNLOAD_FILE_RESPONSE_CODE):
            return
        
        if error_code == self.FILE_NOT_EXISTS:
            print("File not exists, aborting.")
            return
        
        if error_code == self.GOT_DIRECTORY_AS_INPUT:
            print("Please enter a file name, not a directory.")

        if error_code == self.SUCCESS:
            response = self.receive_bytes(response_len)
            file_len = self._parse_download_file_response(response)
            file_content = self.receive_bytes(file_len)
        
            directory_path = input("Enter directory path to save the file in -> ")
            if not os.path.isdir(directory_path):
                print("Path not exists, aborting.")
                return
            
            file_path = os.path.join(directory_path, os.path.basename(file_name))

            if os.path.exists(file_path):
                print("File with the same name already exists on this directory, try to save it in a different directory.")
                return

            try:
                with open(file_path, "wb") as file:
                    file.write(file_content)
            except PermissionError:
                print("Not permitted to write the file on this path, exiting.")
                return

            print("File downloaded successfully!")

    def _handle_create_directory_command(self) -> None:
        """
        Handles the create directory operation, creating an empty directory on the remote server.
        """
        directory_name = input("Enter required directory name. If you want to create a sub directory enter full path (for example omer/new_folder) -> ")

        if directory_name.startswith("/"):
            print("enter relative directory name, and not absolute path (for example, /home/local/dir is not accepted, but moshe/new_dir is accepted)")
            return

        if not directory_name.replace('/','').isalnum():
            print("Invalid directory name, only numbers and letters are allowed for directory name.")
            return

        directory_name_len = len(directory_name)
        request = struct.pack("I", directory_name_len) + directory_name.encode()

        print("sending request")
        self._send_request_header(self.CREATE_DIRECTORY_REQUEST_CODE, request)
        self.send_data(request)

        response_type, error_code, _ = self._parse_response_header()

        if not self._is_correct_response_type(response_type, self.CREATE_DIRECTORY_RESPONSE_CODE):
            return
        
        if error_code == self.SUCCESS:
            print("Directory created!")
            return
        
        if error_code == self.DIRECTORY_ALREADY_EXISTS:
            print("Directory already exists! Try again")
            return

        if error_code == self.INVALID_PATH:
            print("Invalid path! Try again")
            return
        
        print("Got unknown error. Please try again..")
        

    def _handle_upload_file_command(self) -> None:
        """
        Handles the file upload operation, sending the file to the server for storage.
        """
        file_path = input("Enter file path to upload -> ")
        file_name = os.path.basename(file_path)

        if os.path.isdir(file_path):
            print("Please enter a file path, not directory path. Aboring.")
            return

        if not os.path.exists(file_path):
            print("File not exists! aborting.")
            return

        requested_dir = input("Enter directory name to save the file at on the remote server (press enter to save it on the root dir) -> ")
        if requested_dir.startswith("/"):
            print("enter relative directory name, and not absolute path (for example, /home/local/dir is not accepted, but moshe/new_dir is accepted)")
            return
        
        with open(file_path, 'rb') as file:
            file_content = file.read()

        file_len = len(file_content)
        file_name_len = len(file_name)
        requested_dir_len = len(requested_dir)
        request = struct.pack("QII", file_len, file_name_len, requested_dir_len) + file_name.encode() + requested_dir.encode()

        print("sending request")
        self._send_request_header(self.UPLOAD_FILE_REQUEST_CODE, request)
        self.send_data(request)

        response_type, error_code, _ = self._parse_response_header()

        if not self._is_correct_response_type(response_type, self.UPLOAD_FILE_RESPONSE_CODE):
            return

        if error_code == self.DIRECTORY_NOT_EXISTS:
            print("The required path to upload the file is not exists. Try again with a fixed path.")
            return

        if error_code == self.FILE_ALREADY_EXISTS:
            print("File with the same name already uploaded to the server! Try to upload other file.")
            return

        if error_code == self.START_UPLOADING_FILE:
            print("Start uploading file, it might take a while..")
            self.send_file_content(file_content, file_len)
            response_type, error_code, _ = self._parse_response_header()

            if not self._is_correct_response_type(response_type, self.UPLOAD_FILE_RESPONSE_CODE):
                return
            
            if error_code != self.SUCCESS:
                print("Error in uploading file, exiting..")
                return
            print("File uploaded successfully")
    
    def handle_quit_session_command(self) -> None:
        """
        Sends a request to the server to terminate the current session.
        """
        self._send_request_header(self.QUIT_SESSION_REQUEST_CODE)

        print("Exiting session. See you next time.")

    def _start_session(self) -> None:
        """
        Initiates a session where the user can input various commands like uploading, downloading, removing files, 
        listing files, or quitting the session. The session continues until the user inputs the quit command.
        Invalid commands are handled with a prompt to retry.
        """
        request_type = ''
        while request_type != self.QUIT_SESSION_COMMAND:
            request_type = input(
                f"press {self.UPLOAD_FILE_COMMAND} to upload file, {self.DOWNLOAD_FILE_COMMAND} to download file, "  \
                f"{self.REMOVE_FILE_COMMAND} to remove file/directory, {self.LIST_FILES_COMMAND} to list your existing files, " \
                f"{self.CREATE_DIRECTORY_COMMAND} to create directory or {self.QUIT_SESSION_COMMAND} to quit session -> "
            )
            if request_type not in self.command_handlers.keys():
                print("Invalid command, try again")
            else:
                self.command_handlers[request_type]()

    def _create_login_request(self) -> bytes:
        """
        Getting username and password input from the user, then packs the data into a request message.
        
        Returns:
            request (bytes): The packed login request containing the username and password.
        """
        username = input("enter username -> ")
        password = getpass.getpass("enter password -> ")
        request = struct.pack("I", len(username)) + username.encode() + struct.pack("I", len(password)) + password.encode()
        return request
    
    def _parse_list_files_response(self, response: bytes) -> bytes:
        """
        Parses the server's response containing the list of files. 
        
        :param response (bytes): Raw response from the server.
        
        Returns:
            files_list (bytes): The list of files in bytes format.
        """
        files_list_len = struct.unpack("I", response[:self.NUMERIC_FIELD_SIZE])[0]
        response = response[self.NUMERIC_FIELD_SIZE:]
        files_list = response[:files_list_len]
        return files_list

    def _handle_list_files_command(self) -> None:
        """
        Sends a request to the server to retrieve the list of files stored in the user's account.
        Parses and displays the list of files from the server response. 
        """
        self._send_request_header(self.LIST_FILES_REQUEST_CODE)

        response_type, error_code, response_len = self._parse_response_header()
        response = self.receive_bytes(response_len)

        if not self._is_correct_response_type(response_type, self.LIST_FILES_RESPONSE_CODE):
            return

        if error_code != self.SUCCESS:
            print("Got unknown error, aborting.")

        files_list = self._parse_list_files_response(response)
        print(f"Files and directories list - {files_list.decode()}")
