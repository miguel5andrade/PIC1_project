from gpiozero import Servo
from time import sleep
from lcd import *

DEBUG = 1           # 0 - sem deug , 1 - prints no terminal, 2 - prints no LCD e no terminal

# AMEIXA!!! METE OS NOMES COMO QUISERES
servo0 = Servo(5)
servo1 = Servo(0)
servo2 = Servo(1)
servo3 = Servo(12)
servo4 = Servo(7)
servo5 = Servo(14)
servo6 = Servo(15)
servo7 = Servo(3)

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