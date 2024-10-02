import sqlite3
import os

class UserAlreadyExistsException(Exception):
    def __init__(self, username: str) -> None:
        self.username = username
        self.message = f"User '{username}' already exists in the database."
        super().__init__(self.message)


class UserNotExistsException(Exception):
    def __init__(self, username: str) -> None:
        self.username = username
        self.message = f"User '{username}' not exists in the database."
        super().__init__(self.message)

class DataBaseCommunicator:
    """
    This class is responsible for creating a dropbox database and communicate it to add / modify data.
    """
    DB_FILE_NAME = "clients.db"
    CREATE_TABLE_QUERY = '''
                         CREATE TABLE IF NOT EXISTS USERS
                         ( username TEXT PRIMARY KEY,
                         password TEXT NOT NULL  )
                         '''

    def __init__(self) -> None:
        """
        Initializes the database communicator and creates the database file if it does not exist.
        """
        self._create_db_file_if_not_exists()

    def __del__(self) -> None:
        """
        Closes the database connection when the object is destroyed.
        """
        self.conn.close()

    def _create_db_file_if_not_exists(self) -> None:
        """
        Creates the database file and the USERS table if it does not already exist.
        """
        directory_name = os.path.dirname(os.path.abspath(__file__))
        self.db_file_path = os.path.join(directory_name, self.DB_FILE_NAME)
        self.conn = sqlite3.connect(self.db_file_path, check_same_thread=False) 
        self.cursor = self.conn.cursor()

        self.cursor.execute(self.CREATE_TABLE_QUERY)

    def remove_database_file(self) -> None:
        """
        Removes the database file if it exists.
        """
        if os.path.exists(self.db_file_path):
            os.remove(self.db_file_path)

    def remove_data_from_users_table(self) -> None:
        """
        Deletes all entries from the USERS table.
        """
        self.cursor.execute("DELETE FROM USERS;")
        self.conn.commit()
    
    def is_username_exists(self, username: str) -> bool:
        """
        Checks if a username exists in the USERS table.

        :param username (str): The username to check.

        Returns:
            bool: True if the username exists, otherwise False.
        """
        self.cursor.execute("SELECT 1 FROM USERS WHERE username = ?", (username,))
        result = self.cursor.fetchone()
        return result is not None
        
    def create_new_user(self, username: str, password: str) -> None:
        """
        Creates a new user in the USERS table.

        :param username (str): The username of the new user.
        :param password (str): The password of the new user.
        """
        if self.is_username_exists(username):
            raise UserAlreadyExistsException(username)
        self.cursor.execute('INSERT INTO USERS (username, password) VALUES (?, ?)', (username, password))
        self.conn.commit()
    
    def remove_username(self, username: str) -> None:
        """
        Removes a user from the USERS table.

        :param username (str): The username of the user to remove.
        """
        if not self.is_username_exists(username):
            raise UserNotExistsException(username)
        self.cursor.execute('DELETE FROM USERS WHERE username = ?', (username,))
        self.conn.commit()

    def is_password_correct(self, username: str, password: str) -> bool:
        """
        Checks if the provided password matches the stored password (on the database) for the given username.

        :param username (str): The username of the user.
        :param password (str): The password to verify.

        Returns:
            bool: True if the password is correct, otherwise False.
        """
        self.cursor.execute('SELECT 1 FROM USERS WHERE username = ? AND password = ?', (username, password))
        result = self.cursor.fetchone()
        return result is not None
