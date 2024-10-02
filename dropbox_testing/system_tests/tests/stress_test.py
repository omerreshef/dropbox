import os

import subprocess
import sys
from dropbox_testing.system_tests.fixtures import server_startup

NUMBER_OF_CLIENTS_RUNNING_TOGETHER = 50
FILE_SIZE_IN_BYTES = 5 * 1000 * 1000


def run_client_script(client_index, listening_port, file_path):
    return subprocess.Popen(
        [sys.executable, "-c",
        f"""
import os
import shutil
import datetime
import dropbox_system.client.client as client
import dropbox_testing.system_tests.utils as utils
import dropbox_testing.system_tests.constants as constants

def single_client_actions(client_index, listening_port, file_path):
    username = f"client_number_{{client_index}}"
    test_directory = f"/tmp/client_{{client_index}}"
    os.mkdir(test_directory)

    registration_client_instance = client.Client(constants.LOCAL_HOST, listening_port)
    utils.register_new_user(username, registration_client_instance)

    login_client_instance = client.Client(constants.LOCAL_HOST, listening_port)
    print(f"{{datetime.datetime.now().strftime("%H:%M:%S")}} - Uploading a big file and then downloading it for client number {{client_index}}")
    utils.login_and_preform_actions(username, login_client_instance, [
        "L", "C", "newfolder", "U", file_path, "", "L", "D", os.path.basename(file_path), test_directory, "Q"
    ])
    print(f"{{datetime.datetime.now().strftime("%H:%M:%S")}} - Client number {{client_index}} finished")
    shutil.rmtree(test_directory)

single_client_actions({client_index}, {listening_port}, '{file_path}')
        """],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def validate_client_finished_successfully(stdout):
    assert b"File uploaded successfully" in stdout
    assert b"File downloaded successfully" in stdout
    assert b"Directory created" in stdout
    assert b"Exiting session" in stdout

def test_stress(server_startup):
    """
    Connect to the server via multiple clients.
    Perform a stress of requests to the server from all client instances - upload files, download them, create directory..
    Verify all actions are completed successfully.
    """
    listening_port = server_startup
    file_name = "large_file.txt"
    file_directory = "/tmp"
    file_path = os.path.join(file_directory, file_name)
    file_content = "A" * FILE_SIZE_IN_BYTES

    with open(file_path, "w") as file:
        file.write(file_content)

    client_processes = []

    for client_index in range(NUMBER_OF_CLIENTS_RUNNING_TOGETHER):
        proc = run_client_script(client_index, listening_port, file_path)
        client_processes.append(proc)

    for proc in client_processes:
        stdout, _ = proc.communicate()
        assert proc.returncode == 0
        validate_client_finished_successfully(stdout)
    
    os.remove(file_path)
