import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import time


#autenticação para firebase
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {"databaseURL": "https://sekeyrity-c3b78-default-rtdb.europe-west1.firebasedatabase.app/"})



#adicionar um novo user à base de dados 
def create_new_user(user_name, email, card_tag, key_1_acess, key_2_acess, key_3_acess, key_4_acess):

    #antes de registarmos temos de ver se já esta registado
    
    user_exists = ref_users.child(user_name).get()

    #se ja estiver registado bazamos
    if user_exists is not None:
        print(f"User '{user_name}' already registered, failure.")
        return

    new_user = {
        "e-mail": email,
        "card_tag": card_tag,
        "key-01": key_1_acess,
        "key-02": key_2_acess,
        "key-03": key_3_acess,
        "key-04": key_4_acess
    }

    #adicionar novo user
    ref_users.child(user_name).set(new_user)

    # Obtém o valor atual de num_of_users
    num_of_users = ref_root.child("num_of_users").get()

    # Incrementa o número de usuários
    num_of_users += 1

    # Atualiza o valor de num_of_users na base de dados
    ref_root.child("num_of_users").set(num_of_users)

    print(f"User '{user_name}' registered.")
    return  

#apaga user da base de dados
def delete_user(user_name):
    
    #antes de dar-mos delete temos de verificar se o user existe ou não

    
    # Verifica se o usuário existe
    user_exists = ref_users.child(user_name).get()

    if user_exists is not None:
        # Se o usuário existir, exclua-o
        ref_users.child(user_name).delete()
        print(f"User '{user_name}' deleted.")

        # Obtém o valor atual de num_of_users
        num_of_users = ref_root.child("num_of_users").get()
        # Decrementa o número de usuários
        num_of_users -= 1
        # Atualiza o valor de num_of_users na base de dados
        ref_root.child("num_of_users").set(num_of_users)

    else:
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
        print(f"Valor de acesso '{key_id}' do usuário '{user_name}' alterado para '{new_value}'.")
    else:
        # Se o usuário não existir, exiba uma mensagem
        print(f"Usuário '{user_name}' não existe.")

    return
    
