from dispenser import *

servo_init()
i=1
while i<=8:
    rotate_servo(8, "right")
    sleep(4)
    rotate_servo(8, "right")
    sleep(4)
    rotate_servo(8, "left")
    sleep(4)
    rotate_servo(8, "left")
    i += 1