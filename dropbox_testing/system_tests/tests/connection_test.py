from unittest import mock

import dropbox_system.client.client as client
import dropbox_testing.system_tests.constants as constants
import dropbox_testing.system_tests.utils as utils

from dropbox_testing.system_tests.fixtures import server_startup


def test_multiple_clients(server_startup, capfd):
    """
    Connect to the server via multiple clients.
    Preform actions from each client and verify getting the correct repsonses.
    """
    listening_port = server_startup
    username = "client_number_{}"

    for client_index in range(15):
        registration_client_instance = client.Client(constants.LOCAL_HOST, listening_port)

        utils.register_new_user(username.format(client_index), registration_client_instance)

        captured = capfd.readouterr()
        assert "Registered successfully!" in captured.out


    login_client_instances = []
    for _ in range(15):
        login_client_instances.append(client.Client(constants.LOCAL_HOST, listening_port))
    
    for client_index in range(15):
        utils.login_and_preform_actions(username.format(client_index), login_client_instances[client_index], ["L", "Q"])
    
        captured = capfd.readouterr()
        assert "Files and directories list" in captured.out
