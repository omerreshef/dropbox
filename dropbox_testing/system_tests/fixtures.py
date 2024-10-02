import pytest
import threading
import time

import dropbox_testing.system_tests.utils as utils
import dropbox_testing.system_tests.constants as constants
import dropbox_system.server.server as server

@pytest.fixture(scope="session")
def server_startup():
    """
    Before: 
      * Decide a listening port for the server
      * Initiate server instace
      * Remove uploaded files and database info
      * Start server on a thread
    
    After:
      * Remove uploaded files and database info
      * End the server thread
    """
    listening_port = utils.generate_server_listening_port()
    server_instance = server.Server(constants.LOCAL_HOST, listening_port)

    server_instance.remove_all_users_files()
    server_instance.database_communicator.remove_data_from_users_table()

    server_thread = threading.Thread(target=server_instance.start, daemon=True)
    server_thread.start()

    # Wait for server startup
    time.sleep(2)

    yield listening_port

    server_instance.remove_all_users_files()
    server_instance.database_communicator.remove_data_from_users_table()

    server_thread.join(timeout=1)