import unittest
import struct

from dropbox_system.server.request_parser import *


class TestRequestParser(unittest.TestCase):
    DEFAULT_USERNAME = "username"
    DEFAULT_PASSWORD = "password"
    DEFAULT_FILENAME = "file.txt"
    DEFAULT_REQUESTED_DIR = ""
    DEFAULT_FILE_LEN = 500

    def test_parse_regular_register_request(self):
        """
        Check the method parse_register_request.
        Verify the parser is returning the expected parsed result.
        """
        username_len = struct.pack("I", len(self.DEFAULT_USERNAME))
        password_len = struct.pack("I", len(self.DEFAULT_PASSWORD))
        request = username_len + self.DEFAULT_USERNAME.encode() + password_len + self.DEFAULT_PASSWORD.encode()

        parsed_username, parsed_password = parse_register_request(request)
        self.assertEqual(parsed_username, self.DEFAULT_USERNAME)
        self.assertEqual(parsed_password, self.DEFAULT_PASSWORD)

    def test_parse_empty_register_request(self):
        """
        Check the method parse_register_request.
        Verify the parser is returning the expected parsed result even if the request is empty.
        """
        request = struct.pack("I", 0) + struct.pack("I", 0)
        parsed_username, parsed_password = parse_register_request(request)
        self.assertEqual(parsed_username, "")
        self.assertEqual(parsed_password, "")
    
    def test_parse_invalid_register_request(self):
        """
        Check the method parse_register_request.
        Verify the parser is raising the expected error in case of invalid request.
        """
        malformed_request = struct.pack("I", len(self.DEFAULT_USERNAME))
        with self.assertRaises(struct.error):
            parse_register_request(malformed_request)

    def test_parse_regular_login_request(self):
        """
        Check the method parse_login_request.
        Verify the parser is returning the expected parsed result.
        """
        username_len = struct.pack("I", len(self.DEFAULT_USERNAME))
        password_len = struct.pack("I", len(self.DEFAULT_PASSWORD))
        request = username_len + self.DEFAULT_USERNAME.encode() + password_len + self.DEFAULT_PASSWORD.encode()

        parsed_username, parsed_password = parse_login_request(request)
        self.assertEqual(parsed_username, self.DEFAULT_USERNAME)
        self.assertEqual(parsed_password, self.DEFAULT_PASSWORD)

    def test_parse_empty_login_request(self):
        """
        Check the method parse_login_request.
        Verify the parser is returning the expected parsed result even if the request is empty.
        """
        request = struct.pack("I", 0) + struct.pack("I", 0)
        parsed_username, parsed_password = parse_login_request(request)
        self.assertEqual(parsed_username, "")
        self.assertEqual(parsed_password, "")

    def test_parse_invalid_login_request(self):
        """
        Check the method parse_login_request.
        Verify the parser is raising the expected error in case of invalid request.
        """
        malformed_request = struct.pack("I", len(self.DEFAULT_USERNAME))
        with self.assertRaises(struct.error):
            parse_login_request(malformed_request)

    def test_parse_regular_upload_request(self):
        """
        Check the method parse_upload_request.
        Verify the parser is returning the expected parsed result.
        """
        file_len_field = struct.pack("Q", self.DEFAULT_FILE_LEN)
        file_name_len = struct.pack("I", len(self.DEFAULT_FILENAME))
        requested_dir_len = struct.pack("I", len(self.DEFAULT_REQUESTED_DIR))
        request = file_len_field + file_name_len + requested_dir_len + self.DEFAULT_FILENAME.encode() + self.DEFAULT_REQUESTED_DIR.encode()

        parsed_file_len, parsed_file_name, requested_dir = parse_upload_request(request)
        self.assertEqual(parsed_file_len, self.DEFAULT_FILE_LEN)
        self.assertEqual(parsed_file_name, self.DEFAULT_FILENAME)
        self.assertEqual(requested_dir, self.DEFAULT_REQUESTED_DIR)

    def test_parse_upload_request_with_empty_name(self):
        """
        Check the method parse_upload_request.
        Verify the parser is returning the expected parsed result even if the request is empty.
        """
        file_len_field = struct.pack("Q", self.DEFAULT_FILE_LEN)
        requested_dir_len = struct.pack("I", len(self.DEFAULT_REQUESTED_DIR))
        request = file_len_field + struct.pack("I", 0) + requested_dir_len + self.DEFAULT_REQUESTED_DIR.encode()

        parsed_file_len, parsed_file_name, requested_dir = parse_upload_request(request)
        self.assertEqual(parsed_file_len, self.DEFAULT_FILE_LEN)
        self.assertEqual(parsed_file_name, "")
        self.assertEqual(requested_dir, self.DEFAULT_REQUESTED_DIR)

    def test_parse_upload_request_missing_file_name(self):
        """
        Check the method parse_upload_request.
        Verify the parser is raising the expected error in case of invalid request.
        """
        malformed_request = struct.pack("Q", self.DEFAULT_FILE_LEN)
        with self.assertRaises(struct.error):
            parse_upload_request(malformed_request)

    def test_parse_regular_download_request(self):
        """
        Check the method parse_download_request.
        Verify the parser is returning the expected parsed result.
        """
        file_name_len = struct.pack("I", len(self.DEFAULT_FILENAME))
        request = file_name_len + self.DEFAULT_FILENAME.encode()

        parsed_file_name = parse_download_request(request)
        self.assertEqual(parsed_file_name, self.DEFAULT_FILENAME)

    def test_parse_download_request_empty_file_name(self):
        """
        Check the method parse_download_request.
        Verify the parser is returning the expected parsed result even if the request is empty.
        """
        request = struct.pack("I", 0)
        parsed_file_name = parse_download_request(request)
        self.assertEqual(parsed_file_name, "")

    def test_parse_regular_remove_file_request(self):
        """
        Check the method parse_remove_file_request.
        Verify the parser is returning the expected parsed result.
        """
        file_name_len = struct.pack("I", len(self.DEFAULT_FILENAME))
        request = file_name_len + self.DEFAULT_FILENAME.encode()

        parsed_file_name = parse_remove_file_request(request)
        self.assertEqual(parsed_file_name, self.DEFAULT_FILENAME)

    def test_parse_regular_remove_file_request_empty_file_name(self):
        """
        Check the method parse_remove_file_request.
        Verify the parser is returning the expected parsed result even if the request is empty.
        """
        request = struct.pack("I", 0)
        parsed_file_name = parse_remove_file_request(request)
        self.assertEqual(parsed_file_name, "")

if __name__ == '__main__':
    unittest.main()