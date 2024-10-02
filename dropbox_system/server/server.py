import socket
import threading
import argparse
import shutil
import os

from dropbox_system.server.server_handler import ServerHandler
from dropbox_system.server.db_communicator import DataBaseCommunicator

class Server:
    """
    A dropbox server object that can handle multiple clients simultaneously.
    """
    FILES_DIRECTORY_NAME = "user_files"

    def __init__(self, host: str = '127.0.0.1', port: int = 8080) -> None:
        """
        Initializes the server and binds it to the specified host and port.

        :param host (str): The host address to bind to (default is '127.0.0.1').
        :param port (int): The port number to bind to (default is 8080).
        """
        self.is_initialized = False
        self.host = host
        self.port = port
        self.database_communicator = DataBaseCommunicator()
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.files_directory_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), self.FILES_DIRECTORY_NAME)

        try:
            self.server_socket.bind((self.host, self.port))
        except OSError as e:
            if e.errno == 99:
                print("Cannot assaign the requested address. Exiting.")
            else:
                print(f"{e}, exiting.")
            return

        self.server_socket.listen(60)  # Listen for up to 60 connections
        print(f"Server started and listening on {self.host}:{self.port}")
        self.is_initialized = True

    def remove_all_users_files(self) -> None:
        """Removes all files and directories in the user's files directory."""
        for root, dirs, files in os.walk(self.files_directory_path):
            for file in files:
                file_path = os.path.join(root, file)
                os.remove(file_path)
            for dir in dirs:
                shutil.rmtree(os.path.join(root, dir))

    def handle_client(self, client_socket: socket.socket) -> None:
        """
        Handles a new client connection by creating a new server handler instance for it.

        Args:
            client_socket (socket.socket): The socket object for the connected client.
        """
        handler = ServerHandler(client_socket, self.files_directory_path)
        handler.start_handler()

    def start(self) -> None:
        """Starts the server and listening for new client connections."""
        if not self.is_initialized:
            return

        print("Server is starting...")
        try:
            while True:
                client_socket, _ = self.server_socket.accept()
                client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
                client_thread.start()
                
        except KeyboardInterrupt:
            print("Server is shutting down...")
        finally:
            self.server_socket.close()
            print("Server socket closed.")

def get_arguments_from_user() -> tuple:
    """Parses command line arguments to get network details for starting the server."""
    parser = argparse.ArgumentParser(description="Get network details to start client")
    parser.add_argument('--address', '-i', type=str, default="127.0.0.1", help="Binding address")
    parser.add_argument('--port', '-p', type=int, default=8080, help="Port to connect")
    args = parser.parse_args()
    return args.address, args.port

if __name__ == "__main__":
    address, port = get_arguments_from_user()
    server_instance = Server(address, port)
    server_instance.start()