import random
from unittest import mock

import dropbox_system.client.client as client
import dropbox_testing.system_tests.constants as constants

def generate_server_listening_port():
    return random.randint(5555, 9999)

def register_new_user(username, client_instance):
    with mock.patch('builtins.input', side_effect=[client.Client.REGISTER_CODE, username]):
        with mock.patch('getpass.getpass', side_effect=[constants.DEFAULT_PASSWORD, constants.DEFAULT_PASSWORD]):
            client_instance.handle_user_initial_request()

def login_and_preform_actions(username, client_instance, actions=[]):
    with mock.patch('builtins.input', side_effect=[client.Client.LOGIN_CODE, username]+actions):
        with mock.patch('getpass.getpass', side_effect=[constants.DEFAULT_PASSWORD]):
            client_instance.handle_user_initial_request()