import bcrypt
from modules.db_manager import DatabaseManager

def rehash_passwords():
    db_manager = DatabaseManager()  # Removed DB_CONFIG
    query = "SELECT id, username, password_hash FROM users"
    users = db_manager.execute_query(query, fetch='all')

    for user_id, username, password_hash in users:
        try:
            # Check if the hash is valid
            bcrypt.checkpw("test".encode('utf-8'), password_hash.encode('utf-8'))
        except ValueError:
            # Rehash the password if the hash is invalid
            print(f"Rehashing password for user: {username}")
            new_password = "default_password"  # Replace with a secure default password
            new_hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            update_query = "UPDATE users SET password_hash = %s WHERE id = %s"
            db_manager.execute_query(update_query, (new_hashed_password, user_id))

if __name__ == "__main__":
    rehash_passwords()
