#!/usr/bin/env python

##LIB
# general
from time import sleep
# RFID redear
from mfrc522 import SimpleMFRC522
import random 
# threads
import threading
from multiprocessing import Process, Value, Array

# libs by us
from keypad import *
from online_database import *
from lcd import *
from dispenser import *


"""global variables"""
DEBUG = 1           # 0 - sem deug , 1 - prints no terminal, 2 - prints no LCD e no terminal
loop_flag = 0       # 0 - primeirar iteração, 1 - escrever no teclado, 2 - à espera da tag rfid
number_key_list = []
global while_timer
while_timer = 0     # 0 - not runing, 1 - runing
global key_id
key_id = -1


#RFID reader
reader = SimpleMFRC522()


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




""" RFID reader """
def reader_thread(key_id, while_timer_multi):

    # esperar pela chave passar no leitor
    id, text = reader.read()
    if id:
        key_number = key_id_to_number(id, key_return)
        key_id.value = key_number
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
            elif user_name[:7] == "default":
                lcd.message('Go to our app\nto register')
                sleep(2)
                lcd.clear()

                lcd.message('Forget password?\n')
                user_len = len(user_name)
                password = user_name[7:user_len]

                if DEBUG == 1:
                    print("user password:")
                    print(f"{password}")
                lcd.message(password)
                sleep(10)
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

                                        key_number = key_id.value
                                        if key_number != 0:
                                            lcd.clear()
                                            strore_key(key_number)
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
                            elif is_key_availabel(number_key) == False:
                                lcd.clear()
                                lcd.message('Not availebel')
                                sleep(2)
                                lcd.clear()

                                loop_flag = 0
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
                open_gate(number_key)
                key_gone(number_key, user_name)

            number_key_list.clear()
            loop_flag = 0

## pára o programa com um Ctrl + c
except KeyboardInterrupt:
    if DEBUG == 1:
	    print("Programa terminado")
lcd.clear()
lcd.message('Program stop')
