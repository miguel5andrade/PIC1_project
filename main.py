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
from general import *
import RPi.GPIO as GPIO



"""global variables"""
DEBUG = 1           # 0 - sem prints de deug , 1 - com prints de debug
loop_flag = 0       # 0 - primeirar iteração, 1 - escrever no teclado, 2 - à espera da tag rfid
number_key_list = []
global while_timer
while_timer = 0     # 0 - not runing, 1 - runing
global key_id
key_id = -1



#RFID reader
reader = SimpleMFRC522()


    

def teste_hardware():
    lcd.clear()
    lcd.message('LCD teste')
    print("[LCD]LCD teste")
    lcd_test()

    lcd.clear()
    lcd.message('teste do teclado')
    print("[LCD]teste do teclado")
    teste_valido = teste_teclado()

    if teste_valido == False:
        return False

    lcd.clear()
    lcd.message('teste do servos')
    print("[LCD]teste do servos")
    teste_servos()
    
    lcd.clear()
    lcd.message('teste do RFID\nreader')
    print("[LCD]teste do RFID reader")
    teste_valido = teste_RFID()

    if teste_valido == False:
        return False

    return True

""" RFID reader """
def reader_thread(key_id, while_timer_multi):

    # esperar pela chave passar no leitor
    id, text = reader.read()
    if id:
        key_number = key_id_to_number(id, key_return)
        key_id.value = key_number
        while_timer_multi.value = 0 # stops timer thread
        if DEBUG == 1:
            print("\t[DEBUG]Antes de sair de reader_thread()")
            print(f"\t\tkey_id.value:'{key_id.value}'")
            print(f"\t\twhile_timer_multi.value:'{while_timer_multi.value}'")
            print(f"\t\tid:'{id}'")

    return

def timer():
    global while_timer

    while_timer = 0
    return

def teste_RFID():
    lcd.clear()
    lcd.message('sacan a card')
    print("[LCD]sacan a card")

    thread_stop_after_1min = threading.Timer(20.0, timer)
    thread_stop_after_1min.start()

    # thread de leitura das chaves por RFID
    key_id.value = -1
    while_timer_multi.value = 1 # flag to stop timer thread
    thread_reader = Process(target=reader_thread, args=(key_id, while_timer_multi))
    thread_reader.start()

    while(1):
        if key_id.value != -1:
            lcd.clear()
            return True
        elif while_timer == 0 or while_timer_multi.value == 0:
            lcd.clear()
            return False
        
# lé qual é a chave que doi passada em binario que é enviado por um arduino
def read_pins_from_arduino():
    while(1):
        pin_values = {}
        key = 1
        for pin in GPIO_PINS:
            pin_values[pin] = GPIO.input(pin)
            if pin_values[pin] == 1:
                return key
            key += key

        if while_timer == 0:
            return False


        
    

""" MAIN """
try:
    ## inicializações
    servo_init()        # servos
    key_id = Value('i', 0)    # argumento para a multithread de leitura chaves
    while_timer_multi = Value('i', 0)   # argumento para a multithread de leitura de chaver

    ### Setup para ler atraves do arduino qual a chave que passou
    #Define the GPIO pins according to BCM numbering
    GPIO_PINS = [2, 3, 14, 15]  
    # Use BCM numbering
    GPIO.setmode(GPIO.BCM)
    # Set up each pin as an input with a pull-down resistor
    for pin in GPIO_PINS:
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    teste_valido = teste_hardware()
    
    print("Setup done!")
    
    lcd.clear()
    lcd.clear()
    lcd.message('Setup\ndone!')
    print("[LCD]Setup done!")
    sleep(2)
    lcd.clear()

    ## LOOP
    while True:
        # leitura de cartão do utilizador
        if loop_flag == 0:
            lcd.message('Scan your \ncard')
            print("[LCD]Scan your card")
            sleep(0.5)

            card_id, text = reader.read()
            if card_id:
                loop_flag = 1
            lcd.clear()
            
            if  DEBUG == 1:
                print(f"\t[DEBUG]Reade card ID: '{card_id}")

        # descobre o user_name, se não existir regista ou verifica se tem chaves para devolver
        if loop_flag == 1:
            # se o id não existir na base de dados temos de registalo
            user_name = check_card_id(card_id)
        
            # não existe nenhum utilizador com este cartão
            if user_name == 0 :
                lcd.message('You are not\nregistered')
                print("[LCD]You are not registered")
                sleep(2)

                lcd.clear()
                lcd.message('Would you like\nto register?')
                print("[LCD]Would you like to register?")
                sleep(1)
                loop_flag = 2
            # ainda não acabou o registo
            elif user_name[:7] == "default":
                lcd.message('Go to our app\nto register')
                print("[LCD]Go to our app to register")
                sleep(2)
                lcd.clear()

                lcd.message('Forget password?\n')
                print("[LCD]Forget password?")
                user_len = len(user_name)
                password = user_name[7:user_len]

                
                lcd.message(password)
                print(f"[LCD]{password}")
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
                    print(f"[LCD]Return[green]")
                    lcd.message('Request[red]\n')
                    print(f"[LCD]Request[red]")
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
                                    print("\t[DEBUG]read: # (Return key)")

                                lcd.clear()
                                lcd.clear()
                                lcd.message('Insert the key \nto be returned')
                                print(f"[LCD]Insert the key nto be returned")
                                 # timeout thread
                                while_timer = 1
                                thread_stop_after_1min = threading.Timer(60.0, timer)
                                thread_stop_after_1min.start()

                                # thread de leitura das chaves por RFID
                                # key_id.value = -1
                                # while_timer_multi.value = 1 # flag to stop timer thread
                                # thread_reader = Process(target=reader_thread, args=(key_id, while_timer_multi))
                                # thread_reader.start()

                                key_readed = read_pins_from_arduino()
                                if key_readed == False:
                                    lcd.clear()
                                    lcd.message('Timeout')
                                    print("[LCD]Timeout")
                                    sleep(2)
                                    lcd.clear()
                                    loop_flag = 0
                                    break

                                if key_readed != 0:
                                    lcd.clear()
                                    strore_key(key_readed)
                                    key_back(key_readed, user_name)

                                    lcd.message('Thanks')
                                    sleep(3)
                                    lcd.clear()
                                else:
                                    lcd.clear()
                                    lcd.message('Invalid key')
                                    sleep(3)
                                    lcd.clear()


                                loop_flag = 0
                                break

                            # retirar chave 
                            elif key == "*":
                                if DEBUG == 1:
                                    print("\t[DEBUG]read: * (levar chave)")

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
                        print("[LCD]Open our app and\ninsert this key")
                        sleep(4)

                        password = random.randint(1, 10000)
                        user_name = "default" + str(password)     # argumeto para a thread de registos
                        create_new_user(user_name, "default@gmail.com", card_id, password, False, False, False, False)
                        thread_delete_after_10min = threading.Timer(600.0, delete_user, args= (user_name,password))
                        thread_delete_after_10min.start()

                        lcd.clear()
                        lcd.message('Key:\n')
                        print("[LCD]Key:")
                        #password_text = split_integer_to_list(password)
                        lcd.message(str(password))
                        print(f"[LCD]{str(password)}")
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
                    print("[LCD]time out")
                    sleep(2)
                    lcd.clear()
                        

                    loop_flag = 0
                    break

        # mensagem de inicio do loop de entrega da chave
        elif loop_flag == 3:
            lcd.message('Number of the\nkey?')
            print("[LCD]Number of the\nkey?")
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
                            print("[LCD]Chose a key")

                            sleep(2)

                            lcd.clear()
                            lcd.message("Digited:\n")
                            lcd.message(number_key_list)
                            print(f"[LCD]Digited:{number_key_list}")
                        else:
                            number_key = list_to_integer(number_key_list)
                            if DEBUG == 1:
                                print(f"\t[DEBUG]key number: '{number_key}'")

                            if is_key_number(number_key) == 0 :
                                lcd.clear()
                                lcd.message('Key number [1;4]')
                                print("[LCD]Key number [1;4]")
                                sleep(2)
                                lcd.clear()
                                number_key_list.clear()
                                loop_flag = 3
                                break
                            elif is_key_availabel(number_key) == False:
                                lcd.clear()
                                lcd.message('Not availebel')
                                print("[LCD]Not availebel")
                                sleep(2)
                                lcd.clear()

                                loop_flag = 0
                                break
                            elif requested_key(number_key, user_name):
                                if DEBUG == 1:
                                    print("\t[DEBUG]O utilizador já tem esta chave")

                                lcd.clear()
                                lcd.message('You already have\nthis key')
                                print("[LCD]You already have this key")
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
                        print(f"[LCD]Digited:{number_key_list}")

                
                elif while_timer == 0:
                    lcd.clear()
                    lcd.message('Timeout')
                    print("[LCD]Timeout")
                    sleep(2)
                    lcd.clear()

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
    lcd.clear()
lcd.message('Program stoped')
print("[LCD]Program stoped")

