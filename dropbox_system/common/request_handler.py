import struct
import socket
import struct

from dropbox_system.common.xor_encryption import xor_data

class RequestHandler:
    """
    This class provides a generic methods for sending and receiving requests, headers,
    and file data, with XOR encryption applied for data transfer.
    """
    # The size of all numeric fields on this protocol is uint_32 (4 bytes) except for file_len field (uint_64)
    NUMERIC_FIELD_SIZE = 4
    FILE_LEN_FIELD_SIZE = 8
    REGISTER_REQUEST_CODE = 1000
    LOGIN_REQUEST_CODE = 1001
    QUIT_SESSION_REQUEST_CODE = 1002
    REMOVE_FILE_REQUEST_CODE = 1003
    DOWNLOAD_FILE_REQUEST_CODE = 1004
    UPLOAD_FILE_REQUEST_CODE = 1005
    LIST_FILES_REQUEST_CODE = 1006
    CREATE_DIRECTORY_REQUEST_CODE = 1007
    REGISTER_RESPONE_CODE = 2000
    LOGIN_RESPONSE_CODE = 2001
    QUIT_SESSION_RESPONSE_CODE = 2002
    REMOVE_FILE_RESPONSE_CODE = 2003
    DOWNLOAD_FILE_RESPONSE_CODE = 2004
    UPLOAD_FILE_RESPONSE_CODE = 2005
    LIST_FILES_RESPONSE_CODE = 2006
    CREATE_DIRECTORY_RESPONSE_CODE = 2007
    SUCCESS = 0
    USER_NOT_EXISTS = 1
    USER_NOT_LOGGED_IN = 2
    USER_ALREADY_EXISTS = 3
    FILE_ALREADY_EXISTS = 4
    FILE_NOT_EXISTS = 5
    INCORRECT_PASSWORD = 6
    START_UPLOADING_FILE = 7
    DIRECTORY_ALREADY_EXISTS = 8
    GOT_DIRECTORY_AS_INPUT = 9
    DIRECTORY_NOT_EXISTS = 10

    def __init__(self, sock: socket.socket) -> None:
        """
        Initializes the RequestHandler with a socket.

        :param sock (socket.socket): The socket used for communication.
        """
        self.sock = sock

    def __del__(self):
        """
        Closes the socket when the RequestHandler instance is deleted.
        """
        self.sock.close()

    def send_header(self, data: bytes) -> None:
        """
        Sends a unencrypted raw data header over the socket.

        :param data (bytes): The header data to be sent.
        """
        self.sock.send(data)

    def send_data(self, data: bytes) -> None:
        """
        Sends encrypted data on the socket by applying XOR encryption on the data before transmission.

        Args:
            data (bytes): The data to be encrypted and sent.
        """
        xored_data = xor_data(data)
        self.sock.send(xored_data)

    def receive_numeric_value(self) -> bytes:
        """
        Receives a numeric value from the server by reading 4 bytes from the socket. This value is then
        unpacked into an integer.

        Returns:
            int: The numeric value received from the server.
        """
        received_bytes = self.sock.recv(self.NUMERIC_FIELD_SIZE)
        return struct.unpack('I', received_bytes)[0]
    
    def receive_bytes(self, size: int) -> bytes:
        """
        Receives a specific amount of data from the socket. 
        Handles connection errors and applies XOR decryption to the received data.
        Raises ConnectionError if the socket connection is broken.

        :param size (int): The number of bytes to receive.

        Returns:
            bytes: The decrypted data received from the server.
        """
        buffer = b''
        while len(buffer) < size:
            data = self.sock.recv(size - len(buffer))
            if not data:
                raise ConnectionError("Socket connection broken")
            buffer += data
        return xor_data(buffer)
    
    def send_file_content(self, file_content: bytes, file_size: int) -> None:
        """
        Sends file content to the server in chunks, with XOR encryption applied to the file content.

        :param file_content (bytes): The content of the file to be sent.
        :param file_size (int): The size of the file to be sent.
        """
        total_sent = 0
        xored_data = xor_data(file_content)

        while total_sent < file_size:
            sent = self.sock.send(xored_data[total_sent:total_sent+1000])
            if sent == 0:
                raise RuntimeError("Socket connection broken")

            total_sent += sent
