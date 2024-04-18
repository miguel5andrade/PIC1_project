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
# LCD
import Adafruit_CharLCD as LCD
# DATABASE
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import random 
import threading


"""global variables"""
DEBUG = 1           # 0 - sem deug , 1 - prints no terminal, 2 - prints no LCD e no terminal
loop_flag = 0       # 0 - primeirar iteração, 1 - escrever no teclado, 2 - à espera da tag rfid
number_key_list = []


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
    user_exists = ref_users.child(user_name).get()

    #se ja estiver registado bazamos
    if user_exists is not None:
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
        "have_key": 0
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
    
    sleep(1200)
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
            print("id registed")

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
            lcd.message('Return key ')
            lcd.message(key)
            sleep(2)
            lcd.clear()
        return key
    else:
        print("ERRO: no data in data base")
        if DEBUG >= 2:
            lcd.message('Erro: \nin data base')
        return 0
    
def key_gone(key_number, user_name):

    # Verifica se o usuário existe
    user_exists = ref_users.child(user_name).get()
    print(key_number)
    if user_exists is not None:
        # Se o usuário existir, atualize o valor do acesso especificado
        ref_users.child(user_name).update({"have_key": key_number})
        print(f"O utilizador '{user_name}' levou a chave '{key_number}'.")
    else:
        # Se o usuário não existir, exiba uma mensagem
        print(f"Usuário '{user_name}' não existe.")


""" MAIN """
try:
    ## inicializações
    servo1.min() 
    arg = "default"
    

    print("Setup done!")
    lcd.message('Setup\ndone!')
    sleep(2)
    lcd.clear()

    ## LOOP
    while True:
        # leitura de cartão e registo caso o cartão não estiver na base de dados
        if loop_flag == 0:
            lcd.message('Scan your \ncard')
            sleep(0.5)

            card_id, text = reader.read()
            if card_id:
                loop_flag = 1
            lcd.clear()

        # descobre o user_name, se não existir regista e verifica se tem chaves para devolver
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

                lcd.message('Forget key? Wait \n20min')
                sleep(2)
                lcd.clear()
            # se existir pode querer devolver uma chave ou retirar
            else:
                key_return = have_key(user_name)
                if key_return != 0:
                    strore_key(key_return)
                    key_gone(0, user_name)
                    
                    loop_flag = 0
                else:
                    loop_flag = 3

        # não está registado, registar ou não
        if loop_flag == 2:

            key = read_keypad()
            if key != "nada":
                lcd.clear()
                # quer se registar
                if key == "#":
                    lcd.message('Open our app and\ninsert this key')
                    sleep(4)

                    password = random.randint(1, 10000)
                    create_new_user("default", "default@gmail.com", card_id, password, False, False, False, False)
                    thread_delete_after_20min = threading.Thread(target=delete_user, args= (arg,))
                    thread_delete_after_20min.start()

                    lcd.clear()
                    lcd.message('Key:\n')
                    #password_text = split_integer_to_list(password)
                    lcd.message(str(password))
                    sleep(15)
                    lcd.clear()

                    loop_flag = 0

                # não quer se registar 
                elif key == "*":
                    loop_flag = 0

        # mensagem de inicio do loop de entrega da chave
        elif loop_flag == 3:
            lcd.message('Number of the\nkey?')
            sleep(0.5)
            loop_flag = 4
        
        # ask for key number
        elif loop_flag == 4:
            key = read_keypad()
            if key != "nada":
                # ENTER
                if key == "#":
                    number_key = list_to_integer(number_key_list)
                    if is_key_number(number_key) == 0:
                        lcd.clear()
                        lcd.message('Key number [1;4]')
                        sleep(2)
                        lcd.clear()
                        number_key_list.clear()
                        loop_flag = 3
                    else:
                        loop_flag = 5
                        lcd.clear()
                else:
                    # DELET
                    if key == "*":
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
	print("Programa terminado")