import os

from unittest import mock

import dropbox_system.client.client as client
import dropbox_testing.system_tests.constants as constants
import dropbox_testing.system_tests.utils as utils

from dropbox_testing.system_tests.fixtures import server_startup

def test_upload_and_download_large_file(server_startup, capfd):
    """
    Upload a large file to the server.
    Download the file to another path on the client machine, verify the received content is the expected content.
    """
    listening_port = server_startup
    registration_client_instance = client.Client(constants.LOCAL_HOST, listening_port)
    username = "upload_and_download_large_file_test"
    file_name = "large_file.txt"
    test_directory = "/tmp/large_file"
    downloaded_file_path = os.path.join(test_directory, file_name)
    file_directory = "/tmp"
    file_path = os.path.join(file_directory, file_name)
    file_content = "A"  * 50000000 # 50MB file

    os.mkdir(test_directory)
    with open(file_path, "w") as file:
        file.write(file_content)

    utils.register_new_user(username, registration_client_instance)

    captured = capfd.readouterr()
    assert "Registered successfully!" in captured.out

    login_client_instance = client.Client(constants.LOCAL_HOST, listening_port)

    utils.login_and_preform_actions(username, login_client_instance, ["U", file_path, "", "D", file_name, test_directory, "Q"])

    assert os.path.exists(downloaded_file_path)
    with open(downloaded_file_path, "r") as file:
        assert file.read() == file_content

    os.remove(file_path)
    os.remove(downloaded_file_path)
    os.rmdir(test_directory)
    
    captured = capfd.readouterr()
    assert "File downloaded successfully" in captured.out