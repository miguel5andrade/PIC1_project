from gpiozero import Servo
from time import sleep
from lcd import *

DEBUG = 1           # 0 - sem deug , 1 - prints no terminal, 2 - prints no LCD e no terminal

servo1 = Servo(0)
servo2 = Servo(1)
servo3 = Servo(12)
servo4 = Servo(7)
servo5 = Servo(14)
servo6 = Servo(15)
servo7 = Servo(3)
servo8 = Servo(5)

""" real life -> servo identification
      8

      7
  5       6
1   2   3   4
"""



servos_direc_default = ["right", "left","right", "left"]

"""Dispenser functions"""
def servo_init():
    servo1.mid() 
    servo2.mid() 
    servo3.mid() 
    servo4.mid() 
    servo5.mid() 
    servo6.mid() 
    servo7.mid() 
    servo8.mid() 

def teste_servos():
    rotate_servo(1, "left")
    rotate_servo(2, "left")
    rotate_servo(3, "left")
    rotate_servo(4, "left")
    rotate_servo(5, "left")
    rotate_servo(6, "left")
    rotate_servo(7, "left")
    rotate_servo(8, "left")

    rotate_servo(1, "right")
    rotate_servo(2, "right")
    rotate_servo(3, "right")
    rotate_servo(4, "right")
    rotate_servo(5, "right")
    rotate_servo(6, "right")
    rotate_servo(7, "right")
    rotate_servo(8, "right")


## função que vai tratar da disponibilização de uma chave
def open_gate(key_number):

    if key_number < 1 or key_number > 4:
        print(f"ERRO: you can dispense {key_number} key. key is 1,2,3 or 4")
        return
    
    
    rotate_servo(key_number, servos_direc_default[key_number])

    lcd.message('key dispensed')
    sleep(2)
    lcd.clear()


def strore_key(key_number):

    if key_number < 1 or key_number > 4:
        print(f"ERRO: you can store {key_number} key. key is 1,2,3 or 4")
        return

    rotate_servo(8, "right")

    if key_number < 3:
        rotate_servo(7, "left")
        if key_number == 1:
            rotate_servo(5, "left")
        else:
            rotate_servo(5, "right")
    else:
        rotate_servo(7, "right")
        if key_number == 3:
            rotate_servo(6, "left")
        else:
            rotate_servo(6, "right")

    if DEBUG == 1:
        print(f"\t[DEBUG]key_{key_number} was stored")
    


def rotate_servo(servo_number, direction):

    if DEBUG == 1:
        print(f"\t[DEBUG]Servo {servo_number} rotated to {direction}!!")

    if servo_number == 1:
        if direction == "left":
            servo1.min()
            sleep(2)
            servo1.mid()
            return
        elif direction == "right":
            servo1.max()
            sleep(2)
            servo1.mid()
            return
    if servo_number == 2:
        if direction == "left":
            servo2.min()
            sleep(2)
            servo2.mid()
            return
        elif direction == "right":
            servo2.max()
            sleep(2)
            servo2.mid()
            return
    if servo_number == 3:
        if direction == "left":
            servo3.min()
            sleep(2)
            servo3.mid()
            return
        elif direction == "right":
            servo3.max()
            sleep(2)
            servo3.mid()
            return
    if servo_number == 4:
        if direction == "left":
            servo4.min()
            sleep(2)
            servo4.mid()
            return
        elif direction == "right":
            servo4.max()
            sleep(2)
            servo4.mid()
            return
    if servo_number == 5:
        if direction == "left":
            servo5.min()
            sleep(2)
            servo5.mid()
            return
        elif direction == "right":
            servo5.max()
            sleep(2)
            servo5.mid()
            return
    if servo_number == 6:
        if direction == "left":
            servo6.min()
            sleep(2)
            servo6.mid()
            return
        elif direction == "right":
            servo6.max()
            sleep(2)
            servo6.mid()
            return
    if servo_number == 7:
        if direction == "left":
            servo7.min()
            sleep(2)
            servo7.mid()
            return
        elif direction == "right":
            servo7.max()
            sleep(2)
            servo7.mid()
            return
    if servo_number == 8:
        if direction == "left":
            servo8.min()
            sleep(2)
            servo8.mid()
            return
        elif direction == "right":
            servo8.max()
            sleep(2)
            servo8.mid()
            return