# keypad functions
import RPi.GPIO as GPIO
import time

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