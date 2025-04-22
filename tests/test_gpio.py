from smbus2 import SMBus
import time
import numpy as np

import matplotlib.pyplot as plt
import termplotlib as tpl
import RPi.GPIO as GPIO

#LSB -> MSB
GPIO_PINS = [17, 27, 22, 23, 24,25, 5, 6]
GPIO.setmode(GPIO.BCM)

for GPIO_PIN in GPIO_PINS:
    GPIO.setup(GPIO_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)


while True:
    pinout = [GPIO.input(pin) for pin in GPIO_PINS]

    print(f"Pin out: {pinout}")
    time.sleep(0.1)
