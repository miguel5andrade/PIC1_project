import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from time import sleep
import time

# lcd lib
from lcd import *

#autenticação para firebase
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {"databaseURL": "https://sekeyrity-c3b78-default-rtdb.europe-west1.firebasedatabase.app/"})

ref_root = db.reference("/")
ref_users= db.reference('users')
ref_keys= db.reference('keys')
ref_movement = db.reference('movements')

DEBUG = 1           # 0 - sem deug , 1 - prints no terminal, 2 - prints no LCD e no terminal

#adicionar um novo user à base de dados
def create_new_user(user_name, email, card_id, password, key_1_acess, key_2_acess, key_3_acess, key_4_acess):

    #antes de registarmos temos de ver se já esta registado
    data_password = ref_users.child(user_name).child("password").get()

    #se ja estiver registado bazamos
    if password == data_password:
        if DEBUG == 1:
            print(f"User '{user_name}' already registered, failure.")
        return

    new_user = {
        "card_tag": card_id,
        "e-mail": email,
        "password": password,
        "key-01": key_1_acess,
        "key-02": key_2_acess,
        "key-03": key_3_acess,
        "key-04": key_4_acess,
        "have_key": 0,
        "admin": 0
    }

    #adicionar novo user
    ref_users.child(user_name).set(new_user)

    # Obtém o valor atual de num_of_users
    num_of_users = ref_root.child("num_of_users").get()

    # Incrementa o número de usuários
    num_of_users += 1

    # Atualiza o valor de num_of_users na base de dados
    ref_root.child("num_of_users").set(num_of_users)

    if DEBUG == 1:
        print(f"User '{user_name}' registered.")
    return

#apaga user da base de dados
def delete_user(user_name, password):
    
    # sleep(90)
    #antes de dar-mos delete temos de verificar se o user existe ou não

    # Verifica se o usuário existe
    data_password = ref_users.child(user_name).child("password").get()

    if password == data_password:
        # Se o usuário existir, exclua-o
        ref_users.child(user_name).delete()

        if DEBUG == 1:
            print(f"User '{user_name}' deleted.")

        # Obtém o valor atual de num_of_users
        num_of_users = ref_root.child("num_of_users").get()
        # Decrementa o número de usuários
        num_of_users -= 1
        # Atualiza o valor de num_of_users na base de dados
        ref_root.child("num_of_users").set(num_of_users)

    else:
        if DEBUG == 1:
            # Se o usuário não existir, exiba uma mensagem
            print(f"User '{user_name}' not registered, can't delete.")

    return


#altera as permissões de um user
def change_access(user_name, key_id, new_value):

    # Verifica se o usuário existe
    user_exists = ref_users.child(user_name).get()
    if user_exists is not None:
        # Se o usuário existir, atualize o valor do acesso especificado
        ref_users.child(user_name).update({key_id: new_value})

        if DEBUG == 1:
            print(f"Valor de acesso '{key_id}' do usuário '{user_name}' alterado para '{new_value}'.")
    else:
        if DEBUG == 1:
            # Se o usuário não existir, exiba uma mensagem
            print(f"Usuário '{user_name}' não existe.")

    return

## check if a id is registed
def check_card_id(user_id):
    access = 0 # 0 - deneid, 1 - access

    # Obtém todos os dados do banco de dados
    data = ref_users.get()

    if data:
        for user_name in data.keys():
            id = ref_users.child(user_name).child("card_tag").get()
            if id == user_id:
                access = 1
                break
            else:
                access = 0

    if DEBUG >= 1:
        if access == 0:
            print("id not registed")
        else:
            print(f"id registed with user name:'{user_name}'")

    if access == 0:
        return 0
    else:
        return user_name
    
# check if a user have access to a key
def check_access(user_name, number_key):
    access = 0 # 0 - deneid, 1 - access
    if number_key < 10:
        key_name = "key-0" +  str(number_key)
    else:
        key_name = "key-" +  str(number_key)

    # Obtém todos os dados do banco de dados
    data = ref_users.get()
    if data:
        access = ref_users.child(user_name).child(key_name).get()

        if DEBUG >= 1:
            if access == 0:
                print("denied")
            else:
                print("access")

        if access == False:
            lcd.message('Access \ndenied!')
            sleep(2)
            lcd.clear()
            return 0
        else:
            lcd.message('Access \ngaranted!')
            sleep(2)
            lcd.clear()
            return 1


    else:
        if DEBUG == 1:
            print("ERRO: no data in data base")
        if DEBUG >= 2:
            lcd.message('Erro: \nin data base')
        return 0
    
def have_key(user_name): 
    data = ref_users.get()
    if data:
        key = ref_users.child(user_name).child("have_key").get()

        if key == 0:
            return 0
        else:
            lcd.message('You have this \nkeys:')
            n = len(str(key))
            str_key = str(key)
            for i in range(n):
                if i != 0:
                    lcd.message(',')
                lcd.message(str_key[i])
                
            sleep(4)
        return key
    else:
        if DEBUG == 1:
            print("ERRO: no data in data base")
        if DEBUG >= 2:
            lcd.message('Erro: \nin data base')
        return 0
    
# insert a flag to know that this user has this key
def key_gone(key_number, user_name):

    # Verifica se o usuário existe
    user_exists = ref_users.child(user_name).get()
    if DEBUG == 1:
        print(key_number)
    if user_exists is not None:
        # retirar chave
        have_key = ref_users.child(user_name).child("have_key").get()
        if have_key == 0:
            # Se o usuário existir, atualize o valor do acesso especificado
            ref_users.child(user_name).update({"have_key": key_number})
        else:
            have_key = int(str(have_key) + str(key_number))
            ref_users.child(user_name).update({"have_key": have_key})

        if DEBUG == 1:
            print(f"O utilizador '{user_name}' levou a chave '{key_number}'.")

        if key_number < 10:
            key_id = f"key-0'{key_number}'"
        elif key_number < 100:
            key_id = f"key-'{key_number}'"
        else:
            print("register_movement is not implemented for more than 100 keys")
            return
        
        key_name = "key_" + str(key_number)
        ref_keys.child(key_name).update({"available": False})

        register_movement(user_name, key_id, True, False)
        
    
    else:
        # Se o usuário não existir, exiba uma mensagem
        print(f"Usuário '{user_name}' não existe.")

    return

# remove a flag to know that this user no longer has this key
def key_back(key_number,user_name):
    # Verifica se o usuário existe
    user_exists = ref_users.child(user_name).get()
    if user_exists is not None:
        # retirar chave
        have_key = ref_users.child(user_name).child("have_key").get()

        # meter a flag a zero caso o utilizador não tenha mais chaves
        if int(have_key) < 10:
            ref_users.child(user_name).update({"have_key": 0})

            if DEBUG == 1:
                print("have_key update to 0!!")

        # retirar o numero da chave devolvida da flag
        else:
            buff = ""
            str_have_key = str(have_key)
            n = len(str_have_key)
            for i in range(n):
                if str_have_key[i] != str(key_number):
                    buff = buff + str_have_key[i]
                
            have_key = int(buff)
            ref_users.child(user_name).update({"have_key": have_key})

            if DEBUG == 1:
                print(f"have_key update to '{buff}'!!")

        if key_number < 10:
            key_id = f"key-0'{key_number}'"
        elif key_number < 100:
            key_id = f"key-'{key_number}'"
        else:
            print("register_movement is not implemented for more than 100 keys")
            return
        
        key_name = "key_" + str(key_number)
        ref_keys.child(key_name).update({"available": True})

        register_movement(user_name, key_id, False, True)
        return
    
    else:
        # Se o usuário não existir, exiba uma mensagem
        print(f"Usuário '{user_name}' não existe.")


# key_id é o que é lido no leitor e key_nmeber é a nossa numeração[1,2,3,4]
def key_id_to_number(key_id, key_number):
    valid_key = False
    # Obtém todos os dados do banco de dados
    data = ref_keys.get()
    i = 1

    if data:
        for data_keys_name in data:
            data_keys_id = ref_keys.child(data_keys_name).child("key_id").get()
            if DEBUG == 1:
                print("Comparing this keys")
                print(f"\t'{data_keys_id}'")
                print(f"\t'{key_id}'")

            if key_id == data_keys_id:
                str_key_nember = str(key_number)
                n = len(str_key_nember)
                for j in range(n):
                    if i == int(str_key_nember[j]):
                        valid_key = True
                        return i

                if valid_key != True:
                    if DEBUG == 1:
                        print("Wrong key")
                    
                    lcd.clear()
                    lcd.message('Wrong key')
                    sleep(2)
                    lcd.clear()
                break
            i = i + 1
    return 0

def requested_key(key_number, user_name):
    # Verifica se o usuário existe
    user_exists = ref_users.child(user_name).get()
    if user_exists is not None:
        # retirar chave
        have_key = ref_users.child(user_name).child("have_key").get()

        if have_key != 0:
            str_have_key = str(have_key)
            n = len(str_have_key)
            for i in range(n):
                if str_have_key[i] == str(key_number):
                    return True

    return False


def register_movement(username, key_id, take_key, return_key):
    #temos de criar um novo dentro do nó 'movements' onde registamos: o user, o id da chave que levou, se levou ou entregou a chave e um timestamp.

    now = time.localtime()
    day = str(now.tm_mday).zfill(2)
    month = str(now.tm_mon).zfill(2)
    year = str(now.tm_year)
    hour = str(now.tm_hour).zfill(2)
    minute = str(now.tm_min).zfill(2)
    
    timestamp = f"{day}-{month}-{year} : {hour}-{minute}"

    topic = {
        "username": username,
        "key_id": key_id,
        "take_key": take_key,
        "return_key": return_key
    }

    #adiciona novo nó
    print(timestamp)
    ref_movement.child(timestamp).set(topic)
    return

def is_key_availabel(key_number):

    keys_data = ref_keys.get()
    if keys_data is not None:

        str_key_number = str(key_number)
        key_name = "key_" + str_key_number
        print(key_name)

        available  = ref_keys.child(key_name).child("available").get()    
        return available 
                    
    else:
        print("Erro in is_key_availabel(), keys_data is None")

    return False