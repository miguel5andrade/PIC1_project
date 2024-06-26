# keypad functions
import RPi.GPIO as GPIO
import time
from lcd import *

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

def teste_teclado():
    lcd.clear()
    lcd.message('Prees 1')
    print("[LCD]Prees 1")
    key = "nada"
    while key == "nada":
        key = read_keypad()
    if key != "1":
        print("[ERRO]")
        return False
    
    lcd.clear()
    lcd.message('Prees 2')
    print("[LCD]Prees 2")
    key = "nada"
    while key == "nada":
        key = read_keypad()
    if key != "2":
        print("[ERRO]")
        return False
    
    lcd.clear()
    lcd.message('Prees 3')
    print("[LCD]Prees 3")
    key = "nada"
    while key == "nada":
        key = read_keypad()
    if key != "3":
        print("[ERRO]")
        return False
    
    lcd.clear()
    lcd.message('Prees 4')
    print("[LCD]Prees 4")
    key = "nada"
    while key == "nada":
        key = read_keypad()
    if key != "4":
        print("[ERRO]")
        return False
    
    lcd.clear()
    lcd.message('Prees 5')
    print("[LCD]Prees 5")
    key = "nada"
    while key == "nada":
        key = read_keypad()
    if key != "5":
        print("[ERRO]")
        return False
    
    lcd.clear()
    lcd.message('Prees 6')
    print("[LCD]Prees 6")
    key = "nada"
    while key == "nada":
        key = read_keypad()
    if key != "6":
        print("[ERRO]")
        return False
    
    lcd.clear()
    lcd.message('Prees 7')
    print("[LCD]Prees 7")
    key = "nada"
    while key == "nada":
        key = read_keypad()
    if key != "7":
        print("[ERRO]")
        return False
    
    lcd.clear()
    lcd.message('Prees 8')
    print("[LCD]Prees 8")
    key = "nada"
    while key == "nada":
        key = read_keypad()
    if key != "8":
        print("[ERRO]")
        return False
    
    lcd.clear()
    lcd.message('Prees 9')
    print("[LCD]Prees 9")
    key = "nada"
    while key == "nada":
        key = read_keypad()
    if key != "9":
        print("[ERRO]")
        return False
    
    lcd.clear()
    lcd.message('Prees RED')
    print("[LCD]Prees RED")
    key = "nada"
    while key == "nada":
        key = read_keypad()
    if key != "*":
        print("[ERRO]")
        return False
    
    lcd.clear()
    lcd.message('Prees 0')
    print("[LCD]Prees 0")
    key = "nada"
    while key == "nada":
        key = read_keypad()
    if key != "0":
        print("[ERRO]")
        return False
    
    lcd.clear()
    lcd.message('Prees GREEN')
    print("[LCD]Prees GREEN")
    key = "nada"
    while key == "nada":
        key = read_keypad()
    if key != "#":
        print("[ERRO]")
        return False
    
    return True

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

