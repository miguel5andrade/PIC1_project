import pigpio
from time import sleep
import RPi.GPIO as GPIO  

""" real life -> servo identification
      8

      7
  5       6
1   2   3   4
"""

DEBUG = 1 # debug flag for prints

GPIO.setmode(GPIO.BCM)
GPIO.setup(27, GPIO.OUT) #bit0 de seleção do multiplexer
GPIO.setup(7, GPIO.OUT)  #bit1 de seleção do multiplexer
GPIO.setup(5, GPIO.OUT)  #bit2 de seleção do multiplexer
                         #GPIO12 - PWM for servo

servo_pwm_center = [1600, 1400, 1450, 1500, 1400, 1400, 1500, 1500]
servos_return_default = ["right", "left","right", "left"]

pi = pigpio.pi()
if not pi.connected:
    exit()


# roda um servo para a direção pedida e volta a mete-lo no centro
def rotate_servo(direction, servo):
    servo_og = servo
    mux_escolher_saida(servo)

    if direction == "right":
        pi.set_servo_pulsewidth(12, 1000) # safe anti-clockwise
        print(f"rotate right servo_{servo_og}")
        sleep(2)
        pi.set_servo_pulsewidth(12, servo_pwm_center[servo_og-1]) # centre
        print(f"rotate centre servo_{servo_og}")
        sleep(2)
    elif direction == "left":
        pi.set_servo_pulsewidth(12, 2000) # safe clockwise
        print(f"rotate left servo_{servo_og}")
        sleep(2)
        pi.set_servo_pulsewidth(12, servo_pwm_center[servo_og-1]) # centre
        print(f"rotate centre servo_{servo_og}")
        sleep(2)
    elif direction == "center":
        pi.set_servo_pulsewidth(12, servo_pwm_center[servo_og-1]) # centre
        print(f"rotate centre servo_{servo_og}")
        sleep(2)
    elif direction == "left and stay":
        pi.set_servo_pulsewidth(12, 2000) # safe clockwise
        print(f"rotate left and stay servo_{servo_og}")
        sleep(2)
    elif direction == "right and stay":
        pi.set_servo_pulsewidth(12, 1000) # safe anti-clockwise
        print(f"rotate right and stay servo_{servo_og}")
        sleep(2)

    mux_off()

# testo do sevo sem multiplexer
def teste_servo_direto():
    while (1):
        pi.set_servo_pulsewidth(12, 1000) # safe anti-clockwise
        sleep(2)
        pi.set_servo_pulsewidth(12, 1500) # centre
        sleep(2)
        pi.set_servo_pulsewidth(12, 2000) # safe clockwise
        sleep(2)
        pi.set_servo_pulsewidth(12, 1000) # safe anti-clockwise
        sleep(2)

# teste de cada servo um a um         
def teste_servo_com_multiplexer():
    # rotate("left",1)   # o 1 não pode rodar para a esquerda
    # sleep(2)
    rotate_servo("left",2)
    sleep(2)
    rotate_servo("left",3)
    sleep(2)
    rotate_servo("left",4)
    sleep(2)
    rotate_servo("left",5)
    sleep(2)
    rotate_servo("left",6)
    sleep(2)
    rotate_servo("left",7)
    sleep(2)
    rotate_servo("left",8)
    sleep(2)

    rotate_servo("right",1)
    sleep(2)
    rotate_servo("right",2)
    sleep(2)
    rotate_servo("right",3)
    # rotate_servo("right",4)
    # sleep(2)
    rotate_servo("right",5)
    sleep(2)
    # rotate_servo("right",6)
    # sleep(2)
    rotate_servo("right",7)
    sleep(2)
    rotate_servo("right",8)
    sleep(2)

# mete os bits de seleção a high/logh
def mux_escolher_saida(servo_number):
    if servo_number == 6:
        servo_number = 5
    elif servo_number > 6:
        servo_number -= 1

    # escolher a saida do multiplexer
    binary = bin(servo_number)
    if servo_number <= 1:
        GPIO.output(27, int(binary[2]))       #bit0 - set port/pin value to 1/GPIO.HIGH/True 
        GPIO.output(7, 0)        #bit1 - set port/pin value to 1/GPIO.HIGH/True  
        GPIO.output(5, 0)        #bit2 - set port/pin value to 1/GPIO.HIGH/True  
        if DEBUG == 1:
            print(f"\t[debug] select pins: 00{int(binary[2])}")
    elif servo_number <=3:
        GPIO.output(27, int(binary[3]))       #bit0 - set port/pin value to 1/GPIO.HIGH/True  
        GPIO.output(7, int(binary[2]))        #bit1 - set port/pin value to 1/GPIO.HIGH/True  
        GPIO.output(5, 0)        #bit2 - set port/pin value to 1/GPIO.HIGH/True 
        if DEBUG == 1:
            print(f"\t[debug] select pins: 0{int(binary[3])}{int(binary[2])}")
    else:
        GPIO.output(27, int(binary[4]))       #bit0 - set port/pin value to 1/GPIO.HIGH/True  
        GPIO.output(7, int(binary[3]))        #bit1 - set port/pin value to 1/GPIO.HIGH/True  
        GPIO.output(5, int(binary[2]))        #bit2 - set port/pin value to 1/GPIO.HIGH/True 
        if DEBUG == 1:
            print(f"\t[debug] select pins: {int(binary[4])}{int(binary[3])}{int(binary[2])}")
    sleep(0.5)

# mete todos os bits de seleção do 
def mux_off():
    # desligar a saida
    GPIO.output(27, 0)       #bit0 - set port/pin value to 1/GPIO.HIGH/True  
    GPIO.output(7, 0)        #bit1 - set port/pin value to 1/GPIO.HIGH/True  
    GPIO.output(5, 0)        #bit2 - set port/pin value to 1/GPIO.HIGH/True 

# inicialização dos servos - mete todos na horizontal
def servo_init():
    mux_escolher_saida(1)
    pi.set_servo_pulsewidth(12, servo_pwm_center[0]) # centre
    sleep(1)
    mux_off()

    mux_escolher_saida(2)
    pi.set_servo_pulsewidth(12, servo_pwm_center[1]) # centre
    sleep(1)
    mux_off()

    mux_escolher_saida(3)
    pi.set_servo_pulsewidth(12, servo_pwm_center[2]) # centre
    sleep(1)
    mux_off()

    mux_escolher_saida(4)
    pi.set_servo_pulsewidth(12, servo_pwm_center[3]) # centre
    sleep(1)
    mux_off()

    mux_escolher_saida(5)
    pi.set_servo_pulsewidth(12, servo_pwm_center[4]) # centre
    sleep(1)
    mux_off()

    # mux_escolher_saida(6)
    # pi.set_servo_pulsewidth(12, servo_pwm_center[5]) # centre
    # sleep(1)
    # mux_off()

    mux_escolher_saida(7)
    pi.set_servo_pulsewidth(12, servo_pwm_center[6]) # centre
    sleep(1)
    mux_off()

    mux_escolher_saida(8)
    pi.set_servo_pulsewidth(12, servo_pwm_center[7]) # centre
    sleep(1)
    mux_off()

# movimenta os servos de forma a guardar a chave no sitio certo
def store_key(key_number):
    if key_number < 1 or key_number > 4:
        print(f"ERRO: you can not store {key_number} key. key is 1,2,3 or 4")
        return
    
    rotate_servo("right", 8)
    rotate_servo("left and stay", 8)

    if key_number < 3:
        rotate_servo("left", 7)
        if key_number == 1:
            rotate_servo("left", 5)
        else:
            rotate_servo("right", 5)
    else:
        rotate_servo("right", 7)
        if key_number == 3:
            rotate_servo("left", 6)
        else:
            rotate_servo("right", 6)

    if DEBUG == 1:
        print(f"\t[DEBUG]key_{key_number} was stored")

#
def give_key(key_number):
    if key_number < 1 or key_number > 4:
        print(f"ERRO: you can dispense {key_number} key. key is 1,2,3 or 4")
        return
    
    rotate_servo(servos_return_default[key_number - 1], key_number)    




