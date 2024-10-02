import unittest
import sqlite3

from dropbox_system.server.db_communicator import DataBaseCommunicator, UserAlreadyExistsException, UserNotExistsException


class TestDataBaseCommunicator(unittest.TestCase):
    DEFAULT_USERNAME = "username"
    DEFAULT_PASSWORD = "password"

    def setUp(self):
        # Instead of using file based database, I create memory based db.
        self.db = DataBaseCommunicator()
        self.db.conn = sqlite3.connect(':memory:')
        self.db.cursor = self.db.conn.cursor()
        self.db.cursor.execute(DataBaseCommunicator.CREATE_TABLE_QUERY)
        self.db.conn.commit()

    def tearDown(self):
        self.db.conn.close()

    def test_create_new_user(self):
        """
        Check the method `create_new_user` of DataBaseCommunicator.
        Create new user and verify it is written to the database.
        Then try to create it again and expect to receive error because the user already exists.
        """
        self.assertFalse(self.db.is_username_exists(self.DEFAULT_USERNAME))

        self.db.create_new_user(self.DEFAULT_USERNAME, self.DEFAULT_PASSWORD)
        self.assertTrue(self.db.is_username_exists(self.DEFAULT_USERNAME))

        with self.assertRaises(UserAlreadyExistsException):
            self.db.create_new_user(self.DEFAULT_USERNAME, self.DEFAULT_PASSWORD)

    def test_remove_username(self):     
        """
        Check the method `remove_username` of DataBaseCommunicator.
        Create new user, then remove it.
        Then try to remove it again and expect to receive error because it is not exist.
        """
        self.db.create_new_user(self.DEFAULT_USERNAME, self.DEFAULT_PASSWORD)
        self.assertTrue(self.db.is_username_exists(self.DEFAULT_USERNAME))

        self.db.remove_username(self.DEFAULT_USERNAME)
        self.assertFalse(self.db.is_username_exists(self.DEFAULT_USERNAME))

        with self.assertRaises(UserNotExistsException):
            self.db.remove_username(self.DEFAULT_USERNAME)

    def test_is_username_exists(self):
        """
        Check the method `is_username_exists` of DataBaseCommunicator.
        Verify it returns false for a non existing user.
        Then register a user and verify it returns True for this username.
        """
        self.assertFalse(self.db.is_username_exists(self.DEFAULT_USERNAME))

        self.db.create_new_user(self.DEFAULT_USERNAME, self.DEFAULT_PASSWORD)
        self.assertTrue(self.db.is_username_exists(self.DEFAULT_USERNAME))

    def test_is_password_correct(self):
        """
        Check the method `is_password_correct` of DataBaseCommunicator.
        Register a user and verify it returns True for this username and password.
        Verify it returns false for a wrong password.
        """
        wrong_password = self.DEFAULT_PASSWORD + "blabla"

        self.db.create_new_user(self.DEFAULT_USERNAME, self.DEFAULT_PASSWORD)

        self.assertTrue(self.db.is_password_correct(self.DEFAULT_USERNAME, self.DEFAULT_PASSWORD))

        self.assertFalse(self.db.is_password_correct(self.DEFAULT_USERNAME, wrong_password))

    def test_all_exceptions(self):
        """
        Check the exceptions of DataBaseCommunicator.
        The first one - create twice the same user, expect for UserAlreadyExistsException.
        The second one - remove non existing user, expect for UserNotExistsException
        """
        non_existing_user = self.DEFAULT_USERNAME + "blabla"
        self.db.create_new_user(self.DEFAULT_USERNAME, self.DEFAULT_PASSWORD)

        with self.assertRaises(UserAlreadyExistsException):
            self.db.create_new_user(self.DEFAULT_USERNAME, self.DEFAULT_PASSWORD)

        with self.assertRaises(UserNotExistsException):
            self.db.remove_username(non_existing_user)

if __name__ == '__main__':
    unittest.main()