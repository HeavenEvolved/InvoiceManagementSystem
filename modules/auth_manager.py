import bcrypt
from modules.db_manager import DatabaseManager

class AuthManager:
    """Handles user authentication and password management."""

    def __init__(self):
        self.db_manager = DatabaseManager()

    def hash_password(self, password):
        """Hashes a plain text password."""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def verify_password(self, plain_password, hashed_password):
        """Verifies a plain text password against a hashed password."""
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

    def authenticate_user(self, username, password):
        """Authenticates a user by username and password."""
        user = self.db_manager.execute_query(
            "SELECT id, username, password_hash, first_name, last_name, role_id FROM users WHERE username = %s AND is_active = 1",
            (username,), fetch='one'
        )
        if user and self.verify_password(password, user[2]):
            role_name = self.db_manager.execute_query(
                "SELECT role_name FROM roles WHERE id = %s", (user[5],), fetch='one'
            )[0]
            return {"id": user[0], "name": f"{user[3]} {user[4]}", "role": role_name}
        return None

    def load_user_credentials(self):
        """
        Loads user credentials from the database for authentication.
        """
        query = "SELECT id, username, password_hash, first_name, last_name, role_id FROM users WHERE is_active = 1"
        users_data = self.db_manager.execute_query(query, fetch='all')

        if users_data:
            credentials = {
                "usernames": {},
                "names": {},
                "passwords": {},
                "user_ids": {},
                "roles": {}
            }
            for user_id, username, password_hash, first_name, last_name, role_id in users_data:
                credentials["usernames"][username] = password_hash
                credentials["names"][username] = f"{first_name} {last_name}"
                credentials["user_ids"][username] = user_id

                # Fetch role name
                role_query = "SELECT role_name FROM roles WHERE id = %s"
                role_result = self.db_manager.execute_query(role_query, (role_id,), fetch='one')
                credentials["roles"][username] = role_result[0] if role_result else "unknown"

            return credentials
        return {"usernames": {}, "names": {}, "passwords": {}, "user_ids": {}, "roles": {}}
