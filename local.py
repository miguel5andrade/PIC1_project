import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import sqlite3
import datetime
import time

#autenticação para firebase
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {"databaseURL": "https://sekeyrity-c3b78-default-rtdb.europe-west1.firebasedatabase.app/"})

while True:
   
    # Conexão com a data base SQLite
    conn = sqlite3.connect('local_data_base.db')
    c = conn.cursor()

    # Criar uma tabela SQLite para o número de users
    c.execute('''CREATE TABLE IF NOT EXISTS num_users (
                n_users INTEGER,
                timestamp DATETIME)''')
    conn.commit()


    # Criar uma tabela  SQLite para a info dos users
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                name TEXT,
                card_tag TEXT,
                email TEXT,
                have_key INTEGER,
                key_01 BOOLEAN,
                key_02 BOOLEAN,
                key_03 BOOLEAN,
                key_04 BOOLEAN,
                timestamp DATETIME)''')
    conn.commit()


    
    # Obter os dados do Firebase
    firebase_data = db.reference('/').get()

    # Guardar o número de users na tabela SQLite
    num_users = firebase_data.get('num_of_users', 0)
    c.execute("INSERT INTO num_users (n_users, timestamp) VALUES (?, ?)",
                (num_users, datetime.datetime.now()))
    conn.commit()

    # Guardar os dados de cada user na tabela SQLite
    for name, user_data in firebase_data.get('users', {}).items():
        card_tag = user_data.get('card_tag', '')
        email = user_data.get('e-mail', '')
        have_key = user_data.get('have_key', 0)
        key_01 = user_data.get('key-01', False)
        key_02 = user_data.get('key-02', False)
        key_03 = user_data.get('key-03', False)
        key_04 = user_data.get('key-04', False)


        # Inserir os dados do user na tabela SQLite
        c.execute("INSERT INTO users (name, card_tag, email, have_key, key_01, key_02, key_03, key_04, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (name, card_tag, email, have_key, key_01, key_02, key_03, key_04, datetime.datetime.now()))
        conn.commit()


    # Esperar 24 horas 
    print("Entrou no timer")
    time.sleep(24 * 60 * 60)

    conn.close()