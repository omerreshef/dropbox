import socket
import argparse

from dropbox_system.client.client_handler import ClientHandler

class Client:
    """
    A dropbox client object that connects to a dropbox server.
    """
    REGISTER_CODE = '1'
    LOGIN_CODE = '2'
    INITIAL_REQUEST_EXPLAINATION = "Press 1 to register, 2 to sign in -> "

    def __init__(self, host: str = '127.0.0.1', port: int = 8080) -> None:
        """
        Initializes the client with a specified server address and port, and establishes a socket connection.
        
        Arguments:
        :param host (str): The server's IP address (default is '127.0.0.1').
        :param port (int): The server's port number (default is 8080).
        """
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected = False
        self._connect()
        self.handler = ClientHandler(self.sock)
    
    def __del__(self) -> None:
        """
        Closing the socket when the client object is destroyed.
        """
        self.sock.close()

    def _connect(self) -> None:
        """
        Establishes a connection to the server. Updates the connected attribute to True if successful.
        """
        try:
            self.sock.connect((self.host, self.port))
            self.connected = True
        except Exception as e:
            print(f"Failed connecting to server - {e}")

    def handle_user_initial_request(self) -> None:
        """
        Handles the user's initial request (register or login).
        Based on the user's input, sends the appropriate request to the server.
        """
        print("Statring client")
        request = input(self.INITIAL_REQUEST_EXPLAINATION)

        if request == self.REGISTER_CODE:
            self.handler.send_register_request()
        elif request == self.LOGIN_CODE:
            self.handler.send_login_request()
        else:
            print("Invalid request number, try to connect again please.")
            self.handler.handle_quit_session_command()

def get_arguments_from_user() -> tuple:
    """
    Parses command-line arguments to get the server's IP address and port.
    
    Returns a tuple containing the IP address (str) and port (int).
    """
    parser = argparse.ArgumentParser(description="Get network details to start client")
    parser.add_argument('--address', '-i', type=str, default="127.0.0.1", help="IP address to connect")
    parser.add_argument('--port', '-p', type=int, default=8080, help="Port to connect")
    args = parser.parse_args()
    return args.address, args.port

if __name__ == "__main__":
    address, port = get_arguments_from_user()
    client_instance = Client(address, port)
    if client_instance.connected:
        client_instance.handle_user_initial_request()
