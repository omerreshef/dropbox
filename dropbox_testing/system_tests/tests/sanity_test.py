import tempfile
import time
import os

from unittest import mock

import dropbox_system.client.client as client
import dropbox_testing.system_tests.constants as constants
import dropbox_testing.system_tests.utils as utils

from dropbox_testing.system_tests.fixtures import server_startup

def test_register_sanity(server_startup, capfd):
    """
    Register to the server, verify the registration worked successfully
    """
    listening_port = server_startup
    client_instance = client.Client(constants.LOCAL_HOST, listening_port)
    username = "register_username"

    utils.register_new_user(username, client_instance)

    captured = capfd.readouterr()
    assert "Registered successfully!" in captured.out


def test_login_sanity(server_startup, capfd):
    """
    Register to the server, then login with this user and verify it worked successfully.
    """
    listening_port = server_startup
    username = "login_sanity_user"

    registration_client_instance = client.Client(constants.LOCAL_HOST, listening_port)

    utils.register_new_user(username, registration_client_instance)

    login_client_instance = client.Client(constants.LOCAL_HOST, listening_port)
    utils.login_and_preform_actions(username, login_client_instance, ["Q"])
    
    captured = capfd.readouterr()
    assert "Logged in successfully!" in captured.out

def test_upload_file_sanity(server_startup, capfd):
    """
    Upload a new file to the server and verify it uploaded successfully.
    """
    username = "upload_file_sanity_user"
    listening_port = server_startup
    registration_client_instance = client.Client(constants.LOCAL_HOST, listening_port)

    utils.register_new_user(username, registration_client_instance)

    captured = capfd.readouterr()
    assert "Registered successfully!" in captured.out


    login_client_instance = client.Client(constants.LOCAL_HOST, listening_port)

    with tempfile.NamedTemporaryFile() as temporary_file:
        utils.login_and_preform_actions(username, login_client_instance, ["U", temporary_file.name, "", "Q"])

    time.sleep(1)
    
    captured = capfd.readouterr()
    assert "File uploaded successfully" in captured.out


def test_list_files_sanity(server_startup, capfd):
    """
    Upload a new file to the server, list all files and verify we get the uploaded file name in the list.
    """
    listening_port = server_startup
    username = "list_files_sanity_user"
    file_name = "list_files_test.txt"
    file_directory = "/tmp"
    file_path = os.path.join(file_directory, file_name)

    with open(file_path, "w") as file:
        file.write("aaaa")

    registration_client_instance = client.Client(constants.LOCAL_HOST, listening_port)

    utils.register_new_user(username, registration_client_instance)

    captured = capfd.readouterr()
    assert "Registered successfully!" in captured.out

    login_client_instance = client.Client(constants.LOCAL_HOST, listening_port)
    utils.login_and_preform_actions(username, login_client_instance, ["U", file_path, "", "L", "Q"])
    
    os.remove(file_path)
    
    captured = capfd.readouterr()
    assert "Files and directories list - list_files_test.txt" in captured.out

def test_remove_file_sanity(server_startup, capfd):
    """
    Upload a file to the server and then remove it. Verify the file removed successfully.
    """
    listening_port = server_startup
    username = "remove_file_sanity_user"
    file_name = "remove_file_test.txt"
    file_directory = "/tmp"
    file_path = os.path.join(file_directory, file_name)
    registration_client_instance = client.Client(constants.LOCAL_HOST, listening_port)

    with open(file_path, "w") as file:
        file.write("aaaa")

    utils.register_new_user(username, registration_client_instance)

    captured = capfd.readouterr()
    assert "Registered successfully!" in captured.out

    login_client_instance = client.Client(constants.LOCAL_HOST, listening_port)
    utils.login_and_preform_actions(username, login_client_instance, ["U", file_path, "", "R", file_name, "Q"])
    
    os.remove(file_path)
    
    captured = capfd.readouterr()
    assert "Removed successfully!" in captured.out


def test_download_file_sanity(server_startup, capfd):
    """
    Upload a file to the server, then download it and verify the download completed successfully.
    """
    listening_port = server_startup
    registration_client_instance = client.Client(constants.LOCAL_HOST, listening_port)
    username = "download_file_sanity_user"
    file_name = "lala.txt"
    test_directory = "/tmp/download_file_test"
    downloaded_file_path = os.path.join(test_directory, file_name)
    file_directory = "/tmp"
    file_path = os.path.join(file_directory, file_name)
    file_content = "aaaa"

    os.mkdir(test_directory)
    with open(file_path, "w") as file:
        file.write(file_content)

    utils.register_new_user(username, registration_client_instance)

    captured = capfd.readouterr()
    assert "Registered successfully!" in captured.out

    login_client_instance = client.Client(constants.LOCAL_HOST, listening_port)
    utils.login_and_preform_actions(username, login_client_instance, ["U", file_path, "", "D", file_name, test_directory, "Q"])

    assert os.path.exists(downloaded_file_path)

    os.remove(file_path)
    os.remove(downloaded_file_path)
    os.rmdir(test_directory)
    
    captured = capfd.readouterr()
    assert "File downloaded successfully" in captured.out

