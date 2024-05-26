import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import sqlite3
import time
import os

#autenticação para firebase
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {"databaseURL": "https://sekeyrity-c3b78-default-rtdb.europe-west1.firebasedatabase.app/"})



def dowload_data_base():
    # Conexão com a data base SQLite
    conn = sqlite3.connect('local_data_base.db')
    c = conn.cursor()

    # # Verificar se o arquivo do banco de dados SQLite existe
    if os.path.exists('local_data_base.db'):
        # Conexão com a base de dados SQLite
        conn = sqlite3.connect('local_data_base.db')
        c = conn.cursor()

        # Limpar o conteúdo de todas as tabelas SQLite
        tabelas = [ 'users', 'key_request', 'movements', 'num_of_users', 'num_of_keys', 'keys']
        for tabela in tabelas:
            c.execute(f"DROP TABLE IF EXISTS {tabela};")

        conn.commit()
                

    conn.commit()

    # Criar uma tabela SQLite para o número de users
    c.execute('''CREATE TABLE IF NOT EXISTS num_of_users (
                n_users INTEGER)''')
    conn.commit()

    # Criar uma tabela SQLite para o número de keys
    c.execute('''CREATE TABLE IF NOT EXISTS num_of_keys (
                n_keys INTEGER)''')
    conn.commit()

     # Create a SQLite table for user info
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                name TEXT,
                admin INTEGER,
                card_tag TEXT,
                email TEXT,
                have_key INTEGER,
                key_01 BOOLEAN,
                key_02 BOOLEAN,
                key_03 BOOLEAN,
                key_04 BOOLEANE)''')
    conn.commit()

     # Create a SQLite table for key movements
    c.execute('''CREATE TABLE IF NOT EXISTS movements (
                movement_id TEXT,
                key_id TEXT,
                username TEXT,
                take_key BOOLEAN,
                return_key BOOLEAN,
                return_time DATETIME)''')
    conn.commit()
    
    # Create a SQLite table for key requests
    c.execute('''CREATE TABLE IF NOT EXISTS key_request (
                name TEXT,
                key_01 BOOLEAN,
                key_02 BOOLEAN,
                key_03 BOOLEAN,
                key_04 BOOLEAN,
                timestamp DATETIME)''')
    conn.commit()

     # Create a SQLite table for key 

    c.execute('''CREATE TABLE IF NOT EXISTS keys (
                key TEXT,
                key_id TEXT,
                available BOOLEAN)''')
    conn.commit()

    # Obter os dados do Firebase
    firebase_data = db.reference('/').get()

    # Guardar o número de users na tabela SQLite
    num_of_users = firebase_data.get('num_of_users', 0)
    c.execute("INSERT INTO num_of_users (n_users) VALUES (?)", (num_of_users,))
    conn.commit()

    # Guardar o número de keys na tabela SQLite
    num_of_keys = firebase_data.get('num_of_keys', 0)
    c.execute("INSERT INTO num_of_keys (n_keys) VALUES (?)", (num_of_keys,))
    conn.commit()

    # Guardar os dados de cada user na tabela SQLite
    for name, user_data in firebase_data.get('users', {}).items():
        admin = user_data.get('admin', 0)
        card_tag = user_data.get('card_tag', '')
        email = user_data.get('e-mail', '')
        have_key = user_data.get('have_key', 0)
        key_01 = user_data.get('key-01', False)
        key_02 = user_data.get('key-02', False)
        key_03 = user_data.get('key-03', False)
        key_04 = user_data.get('key-04', False)


        # Inserir os dados do user na tabela SQLite
        c.execute("INSERT INTO users (name, admin, card_tag, email, have_key, key_01, key_02, key_03, key_04) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (name, admin, card_tag, email, have_key, key_01, key_02, key_03, key_04))
        conn.commit()


    # Insert each movement's data into the SQLite table
    for movement_id, movement_data in firebase_data.get('movements', {}).items():
        key_id = movement_data.get('key_id', '')
        username = movement_data.get('username', '')
        take_key = movement_data.get('take_key', False)
        return_key = movement_data.get('return_key', False)
        return_time = movement_data.get('return_time', None)
        timestamp = movement_data.get('timestamp', None)

        # Insert the movement data into the SQLite table
        c.execute("INSERT INTO movements (movement_id, key_id, username, take_key, return_key, return_time) VALUES (?, ?, ?, ?, ?, ?)",
                (movement_id, key_id, username, take_key, return_key, return_time))
        conn.commit()

    for key, key_data in firebase_data.get('keys', {}).items():
        available = key_data.get('available', '')
        key_id = key_data.get('key_id', '')

        c.execute("INSERT INTO keys (key, key_id, available) VALUES (?, ?, ?)",
                (key, key_id, available))
        conn.commit()

    # Insert each key request's data into the SQLite table
    for request_id, request_data in firebase_data.get('key_request', {}).items():
        name = request_data.get('name', '')
        timestamp = request_data.get('timestamp', None)

        # Initialize keys with None as default
        key_01 = key_02 = key_03 = key_04 = False

        # Retrieve keys if they exist
        try:
            key_01 = request_data['key-01']
        except KeyError:
            pass

        try:
            key_02 = request_data['key-02']
        except KeyError:
            pass

        try:
            key_03 = request_data['key-03']
        except KeyError:
            pass

        try:
            key_04 = request_data['key-04']
        except KeyError:
            pass

        # Insert the key request data into the SQLite table
        c.execute("INSERT INTO key_request(name, key_01, key_02, key_03, key_04, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
                (request_id, key_01, key_02, key_03, key_04, timestamp))
        conn.commit()

    # Esperar 24 horas 
    print("Download done")

    conn.close()

# Connect to the SQLite database
def connect_to_database():
    conn = sqlite3.connect('local_data_base.db')
    return conn

# Close the database connection
def close_database_connection(conn):
    conn.close()

# Create tables in SQLite database
def create_tables(conn):
    c = conn.cursor()
    # Create a table for the number of users
    c.execute('''CREATE TABLE IF NOT EXISTS num_of_users (
                n_users INTEGER)''')
    conn.commit()

    # Create a table for the number of keys
    c.execute('''CREATE TABLE IF NOT EXISTS num_of_keys (
                n_keys INTEGER)''')
    conn.commit()

    # Create a table for user info
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                name TEXT,
                admin INTEGER,
                card_tag TEXT,
                email TEXT,
                have_key INTEGER,
                key_01 BOOLEAN,
                key_02 BOOLEAN,
                key_03 BOOLEAN,
                key_04 BOOLEAN,
                timestamp DATETIME)''')
    conn.commit()

    # Create a table for key movements
    c.execute('''CREATE TABLE IF NOT EXISTS movements (
                movement_id TEXT,
                key_id TEXT,
                username TEXT,
                take_key BOOLEAN,
                return_key BOOLEAN,
                return_time DATETIME,
                timestamp DATETIME)''')
    conn.commit()

    # Create a table for key requests
    c.execute('''CREATE TABLE IF NOT EXISTS key_request (
                name TEXT,
                key_01 BOOLEAN,
                key_02 BOOLEAN,
                key_03 BOOLEAN,
                key_04 BOOLEAN,
                timestamp DATETIME)''')
    conn.commit()

    c = conn.cursor()
    # Check if the user exists
    c.execute("SELECT * FROM users WHERE name=?", (user_name,))
    existing_user = c.fetchone()
    if not existing_user:
        print(f"User '{user_name}' does not exist, cannot delete.")
        return

    # Delete user from the users table
    c.execute("DELETE FROM users WHERE name=?", (user_name,))
    conn.commit()
    print(f"User '{user_name}' deleted successfully.")


    c = conn.cursor()
    # Check if the user exists
    c.execute("SELECT * FROM users WHERE name=?", (user_name,))
    existing_user = c.fetchone()
    if not existing_user:
        print(f"User '{user_name}' does not exist.")
        return

    # Update the access permissions for the user
    c.execute("UPDATE users SET ?=? WHERE name=?", (key_id, new_value, user_name))
    conn.commit()
    print(f"Access for key '{key_id}' of user '{user_name}' changed to '{new_value}'.")

# Function to check if a card ID is registered
def check_card_id(conn, user_id):
    c = conn.cursor()
    # Check if the card ID is registered in the database
    c.execute("SELECT name FROM users WHERE card_tag=?", (user_id,))
    user_name = c.fetchone()
    if user_name:
        print(f"Card ID '{user_id}' registered with user name: '{user_name[0]}'")
        return user_name[0]
    else:
        print("Card ID not registered.")
        return None

# Function to check if a user has access to a key
def check_access(conn, user_name, key_number):
    c = conn.cursor()
    # Check if the user has access to the key
    key_field = f"key_0{key_number}" if key_number < 10 else f"key_{key_number}"
    c.execute(f"SELECT {key_field} FROM users WHERE name=?", (user_name,))
    access = c.fetchone()
    if access:
        print("Access granted." if access[0] else "Access denied.")
        return access[0]
    else:
        print("User not found.")
        return False

def have_key(conn, user_name):
    c = conn.cursor()
    # Check if the user has any keys
    c.execute("SELECT have_key FROM users WHERE name=?", (user_name,))
    have_key = c.fetchone()
    if have_key:
        print(f"User '{user_name}' has key(s): {have_key[0]}")
        return have_key[0]
    else:
        print(f"User '{user_name}' not found or has no keys.")
        return None

def key_gone(conn, key_number, user_name):
    c = conn.cursor()
    # Check if the user exists
    c.execute("SELECT * FROM users WHERE name=?", (user_name,))
    existing_user = c.fetchone()
    if not existing_user:
        print(f"User '{user_name}' does not exist.")
        return

    # Update the user's key possession
    c.execute("UPDATE users SET have_key=? WHERE name=?", (key_number, user_name))
    conn.commit()
    print(f"User '{user_name}' took key '{key_number}'.")

def key_back(conn, key_number, user_name):
    c = conn.cursor()
    # Check if the user exists
    c.execute("SELECT * FROM users WHERE name=?", (user_name,))
    existing_user = c.fetchone()
    if not existing_user:
        print(f"User '{user_name}' does not exist.")
        return

    # Update the user's key possession
    c.execute("UPDATE users SET have_key=? WHERE name=?", (0, user_name))
    conn.commit()
    print(f"User '{user_name}' returned key '{key_number}'.")

def key_id_to_number(conn, key_id, key_number):
    c = conn.cursor()
    # Check if the key ID matches the expected key number for the user
    c.execute("SELECT card_tag FROM users WHERE name=?", (user_name,))
    card_id = c.fetchone()
    if card_id and card_id[0] == key_id:
        print(f"Key ID '{key_id}' matches key number '{key_number}' for user '{user_name}'.")
        return key_number
    else:
        print("Key ID does not match the expected key number for the user.")
        return None

def requested_key(conn, key_number, user_name):

    if key_number < 10:
        key_id = f"0{key_number}"
    else:
        print("register_movement is not implemented for more than 100 keys")
        return

    c = conn.cursor()
    # Check if the user has requested the key
    c.execute(f"SELECT key_{key_id} FROM users WHERE name=?", (user_name,))
    requested = c.fetchone()
    if requested:
        requested = requested[0]
        if requested:
            print(f"User '{user_name}' has requested key '{key_number}'.")
            return True
        else:
            print(f"User '{user_name}' has not requested key '{key_number}'.")
            return False
    else:
        print(f"User '{user_name}' not found or has not requested any keys.")
        return False

def register_out_movement(conn, username, key_id, take_key, return_key):
    c = conn.cursor()
    # Register key movement
    movement_id = str(time.time())
    c.execute("INSERT INTO movements (movement_id, key_id, username, take_key, return_key, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
              (movement_id, key_id, username, take_key, return_key, time.time()))
    conn.commit()
    print(f"Registered movement: User '{username}' {'took' if take_key else 'returned'} key '{key_id}'.")

def register_in_movement(conn, key_id): 
    
    c = conn.cursor()
    # Find the last movement associated with the key ID
    c.execute("SELECT * FROM movements WHERE key_id=? ORDER BY timestamp DESC LIMIT 1", (key_id,))
    last_movement = c.fetchone()
    if last_movement:
        movement_id = str(time.time())
        # Register the return movement for the key
        c.execute("INSERT INTO movements (movement_id, key_id, username, take_key, return_key, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
                  (movement_id, key_id, last_movement[2], False, True, time.time()))
        conn.commit()
        print(f"Registered return movement for key '{key_id}'.")
    else:
        print(f"No previous movement found for key '{key_id}'.")

def is_key_available(conn, key_number):


    
    if key_number < 10:
        key_id = f"key_{key_number}"
    else:
        print("register_movement is not implemented for more than 100 keys")
        return
  

    c = conn.cursor()
    # Check if the key is available
    c.execute(f"SELECT available FROM keys WHERE key=?", (key_id,))
    available = c.fetchone()
    if available:
        available = available[0]
        if available:
            print(f"Key '{key_id}' is available.")
            return True
        else:
            print(f"Key '{key_id}' is not available.")
            return False
    else:
        print("Key not found.")
        return False

def main():
    #dowload_data_base()
    conn = connect_to_database()
    oi = is_key_available(conn, 1)
    close_database_connection(conn)
    print(oi)

if __name__ == "__main__":
    main()

