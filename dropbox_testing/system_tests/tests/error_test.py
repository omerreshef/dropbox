import tempfile
import time
import os

from unittest import mock

import dropbox_system.client.client as client
import dropbox_testing.system_tests.utils as utils
import dropbox_testing.system_tests.constants as constants

from dropbox_testing.system_tests.fixtures import server_startup

def test_login_with_non_existing_user(server_startup, capfd):
    """
    Login with non existing username to the server,
    Verify getting the correct response from the server.
    """
    listening_port = server_startup
    client_instance = client.Client(constants.LOCAL_HOST, listening_port)
    non_existing_username = "non_existing"

    utils.login_and_preform_actions(non_existing_username, client_instance)
    
    captured = capfd.readouterr()
    assert "Username not exists! exiting" in captured.out

def test_upload_non_existing_file(server_startup, capfd):
    """
    Upload to the server a file that not exists on the local machine,
    Verify getting the correct error on the client software.
    """
    username = "upload_non_existing_file_test"
    listening_port = server_startup
    registration_client_instance = client.Client(constants.LOCAL_HOST, listening_port)
    non_existing_file_name = "/tmp/non_existing"

    utils.register_new_user(username, registration_client_instance)

    captured = capfd.readouterr()
    assert "Registered successfully!" in captured.out

    login_client_instance = client.Client(constants.LOCAL_HOST, listening_port)

    utils.login_and_preform_actions(username, login_client_instance, ["U", non_existing_file_name, "Q"])
    
    captured = capfd.readouterr()
    assert "File not exists! aborting." in captured.out

def test_download_non_existing_file(server_startup, capfd):
    """
    Download from the server a file that not exists,
    Verify getting the correct response from the server.
    """
    username = "download_non_existing_file_test"
    listening_port = server_startup
    registration_client_instance = client.Client(constants.LOCAL_HOST, listening_port)
    non_existing_file_to_download = "non_existing"

    utils.register_new_user(username, registration_client_instance)

    captured = capfd.readouterr()
    assert "Registered successfully!" in captured.out

    login_client_instance = client.Client(constants.LOCAL_HOST, listening_port)
    
    utils.login_and_preform_actions(username, login_client_instance, ["D", non_existing_file_to_download, "Q"])
    
    captured = capfd.readouterr()
    assert "File not exists, aborting." in captured.out

