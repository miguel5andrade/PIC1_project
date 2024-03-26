import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

#autenticação para firebase
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {"databaseURL": "https://sekeyrity-c3b78-default-rtdb.europe-west1.firebasedatabase.app/"})



#adicionar um novo user à base de dados 
def create_new_user(user_name, key_1_acess, key_2_acess, key_3_acess, key_4_acess):

    new_user = {
        "key_1": key_1_acess,
        "key_2": key_2_acess,
        "key_3": key_3_acess,
        "key_4": key_4_acess
    }

    #adicionar novo user
    ref_users.child(user_name).set(new_user)

    # Obtém o valor atual de num_of_users
    num_of_users = ref_root.child("num_of_users").get()

    # Incrementa o número de usuários
    num_of_users += 1

    # Atualiza o valor de num_of_users na base de dados
    ref_root.child("num_of_users").set(num_of_users)

    print(num_of_users)
    return  

#apaga user da base de dados
def delete_user(user_name):
    
    ref_users.child(user_name).delete()


    # Obtém o valor atual de num_of_users
    num_of_users = ref_root.child("num_of_users").get()

    # Decrementa o número de usuários
    num_of_users -= 1

    # Atualiza o valor de num_of_users na base de dados
    ref_root.child("num_of_users").set(num_of_users)
    return


ref_root = db.reference("/")
ref_users= db.reference('users')

create_new_user("Mike", True, True, False, False)