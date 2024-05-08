#!/usr/bin/env python

##LIB
# general
from time import sleep
import time
# servo
from gpiozero import Servo
# RFID redear
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import queue
# LCD
import Adafruit_CharLCD as LCD
# DATABASE
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import random 
# threads
import threading
from multiprocessing import Process, Value, Array


"""global variables"""
DEBUG = 1           # 0 - sem deug , 1 - prints no terminal, 2 - prints no LCD e no terminal
loop_flag = 0       # 0 - primeirar iteração, 1 - escrever no teclado, 2 - à espera da tag rfid
number_key_list = []
global while_timer
while_timer = 0     # 0 - not runing, 1 - runing
global key_id
key_id = -1


"""Setup"""
#servo          ######### ALTERAR OS PINOS ###############
servo1 = Servo(14)
# servo2 = Servo(14)
# servo[3] = Servo(14)
# servo4 = Servo(14)
# servo5 = Servo(14)
# servo6 = Servo(14)
# servo7 = Servo(14)

#RFID reader
reader = SimpleMFRC522()

#LCD
# Raspberry Pi pin setup
lcd_rs = 4
lcd_en = 24
lcd_d4 = 23
lcd_d5 = 17
lcd_d6 = 18
lcd_d7 = 22
lcd_backlight = 2

# Define LCD column and row size for 16x2 LCD.
lcd_columns = 16
lcd_rows = 2

lcd = LCD.Adafruit_CharLCD(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7, lcd_columns, lcd_rows, lcd_backlight)

#teclado
L1 = 16
L2 = 20
L3 = 21
L4 = 6

C1 = 13
C2 = 19
C3 = 26

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

GPIO.setup(L1, GPIO.OUT)
GPIO.setup(L2, GPIO.OUT)
GPIO.setup(L3, GPIO.OUT)
GPIO.setup(L4, GPIO.OUT)

GPIO.setup(C1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(C2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(C3, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

#autenticação para firebase
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {"databaseURL": "https://sekeyrity-c3b78-default-rtdb.europe-west1.firebasedatabase.app/"})

#referências
ref_root = db.reference("/")
ref_users= db.reference('users')
ref_keys= db.reference('keys')
ref_movement = db.reference('movements')

"""General"""
def list_to_integer(list_int):
    # Convert each integer to a string and concatenate them
    concatenated_string = ''.join(str(num) for num in list_int)

    # Convert the concatenated string back to an integer
    resulting_integer = int(concatenated_string)
    return resulting_integer

def split_integer_to_list(integer):
    # Convert the integer to a string
    integer_str = str(integer)
    
    # Convert each character back to an integer and collect them in a list
    integer_list = [int(char) for char in integer_str]
    
    return integer_list


"""Dispenser functions"""
## função que vai tratar da disponibilização de uma chave
def open_gate():

    ##### POR MODIFICAR ############################################################

    servo1.max()
    if DEBUG == 1:
        print("gate open")
    if DEBUG >= 2:
        lcd.message('gate \nopen!')
        sleep(2)
        lcd.clear()

    sleep(3)

    servo1.min()
    if DEBUG == 1:
        print("gate close")
    if DEBUG >= 2:
        lcd.message('gate \nclose!')
        sleep(2)
        lcd.clear()

def strore_key(key_number):
    servo1.max()
    ############### por fazer ################


"""KEYPAD functions"""
def readLine(line, characters):
    GPIO.output(line, GPIO.HIGH)
    if(GPIO.input(C1) == 1):
        #print(characters[0])
        GPIO.output(line, GPIO.LOW)
        return characters[0]
    if(GPIO.input(C2) == 1):
        #print(characters[1])
        GPIO.output(line, GPIO.LOW)
        return characters[1]
    if(GPIO.input(C3) == 1):
        #print(characters[2])
        GPIO.output(line, GPIO.LOW)
        return characters[2]
    GPIO.output(line, GPIO.LOW)
    return "nada"

def read_keypad():
    key = readLine(L1, ["1", "2", "3"])
    if key != "nada":
        time.sleep(0.2)
        return key
    key = readLine(L2, ["4", "5", "6"])
    if key != "nada":
        time.sleep(0.2)
        return key
    key = readLine(L3, ["7", "8", "9"])
    if key != "nada":
        time.sleep(0.2)
        return key
    key = readLine(L4, ["*", "0", "#"])
    if key != "nada":
        time.sleep(0.2)
        return key
    time.sleep(0.2)
    return "nada"

def is_key_number(number):
    if number > 4 or number < 1:
        return 0
    else:
        return 1


"""DATABASE functions"""
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
    else:
        # Se o usuário não existir, exiba uma mensagem
        print(f"Usuário '{user_name}' não existe.")

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


# key_id é o que é lido no leitor e key_nmeber é a nossa numeração[1,2,3,4]
def key_id_to_number(key_id, key_number):
    valid_key = False
    # Obtém todos os dados do banco de dados
    data = ref_keys.get()
    i = 1

    if data:
        for data_keys_name in data:
            data_keys_id = ref_keys.child(data_keys_name).get()
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



""" RFID reader """
def reader_thread(key_id, while_timer_multi):

    # esperar pela chave passar no leitor
    id, text = reader.read()
    if id:
        key_id.value = id
        while_timer_multi.value = 0 # stops timer thread
        if DEBUG == 1:
            print("Antes de sair de reader_thread()")
            print(f"\tkey_id.value:'{key_id.value}'")
            print(f"\twhile_timer_multi.value:'{while_timer_multi.value}'")
            print(f"\tid:'{id}'")

    return

def timer():
    global while_timer

    while_timer = 0
    return
    


""" MAIN """
try:
    ## inicializações
    servo1.min()        # servos
    key_id = Value('i', 0)    # argumento para a multithread de leitura chaves
    while_timer_multi = Value('i', 0)   # argumento para a multithread de leitura de chaver
    
    if DEBUG == 1:
        print("Setup done!")
    
    lcd.clear()
    lcd.clear()
    lcd.message('Setup\ndone!')
    sleep(2)
    lcd.clear()

    ## LOOP
    while True:
        # leitura de cartão do utilizador
        if loop_flag == 0:
            lcd.message('Scan your \ncard')
            sleep(0.5)

            card_id, text = reader.read()
            if card_id:
                loop_flag = 1
            lcd.clear()
            
            if  DEBUG == 1:
                print(f"Card ID: '{card_id}")

        # descobre o user_name, se não existir regista ou verifica se tem chaves para devolver
        if loop_flag == 1:
            # se o id não existir na base de dados temos de registalo
            user_name = check_card_id(card_id)
        
            # não existe nenhum utilizador com este cartão
            if user_name == 0 :
                lcd.message('You are not\nregistered')
                sleep(2)

                lcd.clear()
                lcd.message('Would you like\nto register?')
                sleep(1)
                loop_flag = 2
            # ainda não acabou o registo
            elif user_name == "default":
                lcd.message('Go to our app\nto register')
                sleep(2)
                lcd.clear()

                lcd.message('Forget key? Wait \n10min')
                sleep(2)
                lcd.clear()

                loop_flag = 0
            # se existir pode querer devolver uma chave ou retirar
            else:
                key_return = have_key(user_name) # verificação se o user tem uma chave
                if key_return != 0:
                    lcd.clear()
                    lcd.clear()
                    lcd.message('Return[green]\n')
                    lcd.message('Request[red]\n')
                    # timeout thread
                    while_timer = 1
                    thread_stop_after_1min = threading.Timer(60.0, timer)
                    thread_stop_after_1min.start()

                    while(1):
                        key = read_keypad()
                        if key != "nada":
                            lcd.clear()
                            thread_stop_after_1min.cancel() # stop timeout timer

                            # quer devolver uma chave
                            if key == "#":
                                if DEBUG == 1:
                                    print("read: # (Return key)")

                                lcd.clear()
                                lcd.clear()
                                lcd.message('Insert the key \nto be returned')
                                 # timeout thread
                                while_timer = 1
                                thread_stop_after_1min = threading.Timer(60.0, timer)
                                thread_stop_after_1min.start()

                                # thread de leitura das chaves por RFID
                                key_id.value = -1
                                while_timer_multi.value = 1 # flag to stop timer thread
                                thread_reader = Process(target=reader_thread, args=(key_id, while_timer_multi))
                                thread_reader.start()

                                while(1):
                                    if key_id.value != -1:
                                        if DEBUG == 1:
                                            print("read somthing")
                                            print(key_id.value)

                                        thread_stop_after_1min.cancel()

                                        key_number = key_id_to_number(key_id.value, key_return)

                                        if key_number != 0:
                                            lcd.clear()
                                            strore_key(key_return)
                                            key_back(key_number, user_name)

                                            lcd.message('Thanks')
                                            sleep(3)
                                            lcd.clear()
                                        else:
                                            lcd.clear()
                                            lcd.message('Invalid key')
                                            sleep(3)
                                            lcd.clear()
                                        break
                                    if while_timer == 0 or while_timer_multi.value == 0:
                                        if DEBUG == 1:
                                            print("time out")
                                            print(key_id)

                                        lcd.clear()
                                        lcd.message('Timeout')
                                        sleep(2)
                                        lcd.clear()

                                        thread_reader.terminate()
                                        break


                                loop_flag = 0
                                break

                            # retirar chave 
                            elif key == "*":
                                if DEBUG == 1:
                                    print("read: * (levar chave)")

                                loop_flag = 3
                                break
                else:
                    loop_flag = 3


        # não está registado -> registar ou não
        if loop_flag == 2:
            # timeout thread
            while_timer = 1
            thread_stop_after_1min = threading.Timer(60.0, timer)
            thread_stop_after_1min.start()

            while(1):
                key = read_keypad()
                if key != "nada":
                    lcd.clear()
                    thread_stop_after_1min.cancel() # stop timeout timer

                    # quer se registar
                    if key == "#":
                        lcd.message('Open our app and\ninsert this key')
                        sleep(4)

                        password = random.randint(1, 10000)
                        user_name = "default" + str(password)     # argumeto para a thread de registos
                        create_new_user(user_name, "default@gmail.com", card_id, password, False, False, False, False)
                        thread_delete_after_10min = threading.Timer(600.0, delete_user, args= (user_name,password))
                        thread_delete_after_10min.start()

                        lcd.clear()
                        lcd.message('Key:\n')
                        #password_text = split_integer_to_list(password)
                        lcd.message(str(password))
                        sleep(15)
                        lcd.clear()

                        loop_flag = 0
                        break

                    # não quer se registar 
                    elif key == "*":
                        loop_flag = 0
                        break

                elif while_timer == 0:
                    lcd.clear()
                    lcd.message('Timeout')
                    sleep(2)
                    lcd.clear()
                    if DEBUG == 1:
                        print("time out")
                        print(key_id)

                    loop_flag = 0
                    break

        # mensagem de inicio do loop de entrega da chave
        elif loop_flag == 3:
            lcd.message('Number of the\nkey?')
            sleep(0.5)
            loop_flag = 4
        
        # ask for key number
        elif loop_flag == 4:
            # timeout thread
            while_timer = 1
            thread_stop_after_1min = threading.Timer(60.0, timer)
            thread_stop_after_1min.start()

            while(1):
                key = read_keypad()
                if key != "nada":
                    thread_stop_after_1min.cancel() # stop timeout timer

                    # ENTER
                    if key == "#":
                        if not number_key_list:
                            lcd.clear()
                            lcd.message('Chose a key')
                            sleep(2)
                            lcd.clear()
                            lcd.message("Digited:\n")
                            lcd.message(number_key_list)
                        else:
                            number_key = list_to_integer(number_key_list)
                            if DEBUG == 1:
                                print(f"key number: '{number_key}'")

                            if is_key_number(number_key) == 0 :
                                lcd.clear()
                                lcd.message('Key number [1;4]')
                                sleep(2)
                                lcd.clear()
                                number_key_list.clear()
                                loop_flag = 3
                                break
                            elif requested_key(number_key, user_name):
                                if DEBUG == 1:
                                    print("O utilizador já tem esta chave")

                                lcd.clear()
                                lcd.message('You already have\nthis key')
                                sleep(2)
                                lcd.clear()
                                number_key_list.clear()
                                loop_flag = 3
                                break
                            else:
                                loop_flag = 5
                                lcd.clear()
                                break
                    else:
                        # DELET
                        if key == "*":
                            if not number_key_list:
                                loop_flag = 0
                                break
                            else:
                                number_key_list.pop()
                        # number
                        else:
                            number_key_list.append(key)
                        lcd.clear()
                        lcd.clear()
                        lcd.message("Digited:\n")
                        lcd.message(number_key_list)

                    if DEBUG == 1:
                        print(number_key_list)
                
                elif while_timer == 0:
                    lcd.clear()
                    lcd.message('Timeout')
                    sleep(2)
                    lcd.clear()
                    if DEBUG == 1:
                        print("time out")
                        print(key_id)

                    loop_flag = 0
                    break

        # check access of this key
        elif loop_flag == 5:
            access = check_access(user_name, number_key)

            if access == True:
                open_gate()
                key_gone(number_key, user_name)

            number_key_list.clear()
            loop_flag = 0

## pára o programa com um Ctrl + c
except KeyboardInterrupt:
    if DEBUG == 1:
	    print("Programa terminado")