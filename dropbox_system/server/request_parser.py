"""
This module contains functions for parsing different binary requests received from the user.

Each parsing function extracts the relevant information from a byte stream according to 
dropbox protocol.

Functions:
- parse_register_request: Parses a registration request to extract the username and password.
- parse_login_request: Parses a login request to extract the username and password.
- parse_upload_request: Parses a file upload request to extract the file length and name.
- parse_download_request: Parses a file download request to extract the file name.
- parse_remove_file_request: Parses a file removal request to extract the file name.
"""

import struct
import struct

from dropbox_system.common.request_handler import RequestHandler

NUMERIC_FIELD_SIZE = RequestHandler.NUMERIC_FIELD_SIZE
FILE_LEN_FIELD_SIZE = RequestHandler.FILE_LEN_FIELD_SIZE

def parse_register_request(request: bytes) -> tuple:
    username_len = struct.unpack("I", request[:NUMERIC_FIELD_SIZE])[0]
    request = request[NUMERIC_FIELD_SIZE:]
    username = request[:username_len]
    request = request[username_len:]
    password_len = struct.unpack("I", request[:NUMERIC_FIELD_SIZE])[0]
    request = request[NUMERIC_FIELD_SIZE:]
    password = request[:password_len]
    return username.decode(), password.decode()

def parse_login_request(request: bytes) -> tuple:
    username_len = struct.unpack("I", request[:NUMERIC_FIELD_SIZE])[0]
    request = request[NUMERIC_FIELD_SIZE:]
    username = request[:username_len]
    request = request[username_len:]
    password_len = struct.unpack("I", request[:NUMERIC_FIELD_SIZE])[0]
    request = request[NUMERIC_FIELD_SIZE:]
    password = request[:password_len]
    return username.decode(), password.decode()

def parse_upload_request(request: bytes) -> tuple:
    file_len = struct.unpack("Q", request[:FILE_LEN_FIELD_SIZE])[0]
    request = request[FILE_LEN_FIELD_SIZE:]
    file_name_len = struct.unpack("I", request[:NUMERIC_FIELD_SIZE])[0]
    request = request[NUMERIC_FIELD_SIZE:]
    requested_dir_len = struct.unpack("I", request[:NUMERIC_FIELD_SIZE])[0]
    request = request[NUMERIC_FIELD_SIZE:]
    file_name = request[:file_name_len]
    request = request[file_name_len:]
    requested_dir = request[:requested_dir_len]
    return file_len, file_name.decode(), requested_dir.decode()

def parse_download_request(request: bytes) -> str:
    file_name_len = struct.unpack("I", request[:NUMERIC_FIELD_SIZE])[0]
    request = request[NUMERIC_FIELD_SIZE:]
    file_name = request[:file_name_len]
    return file_name.decode()

def parse_remove_file_request(request: bytes) -> str:
    file_name_len = struct.unpack("I", request[:NUMERIC_FIELD_SIZE])[0]
    request = request[NUMERIC_FIELD_SIZE:]
    file_name = request[:file_name_len]
    return file_name.decode()

def parse_create_directory_request(request: bytes) -> str:
    directory_name_len = struct.unpack("I", request[:NUMERIC_FIELD_SIZE])[0]
    request = request[NUMERIC_FIELD_SIZE:]
    directory_name = request[:directory_name_len]
    return directory_name.decode()
