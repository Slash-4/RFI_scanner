import RPi.GPIO as GPIO
import time


GPIO.setmode(GPIO.BCM)

GPIO.setup(17, GPIO.OUT)
GPIO.setup(27, GPIO.OUT)
GPIO.setup(22, GPIO.OUT)

green =  17
yellow = 27
red = 22

def blink():
    GPIO.output(green, GPIO.LOW)
    GPIO.output(red, GPIO.LOW)
    GPIO.output(yellow, GPIO.LOW)

    time.sleep(0.5)

    GPIO.output(green, GPIO.HIGH)
    
    time.sleep(1)

    GPIO.output(yellow, GPIO.HIGH)

    time.sleep(1)

    GPIO.output(red, GPIO.HIGH)

    time.sleep(1)

    GPIO.output(green, GPIO.LOW)
    GPIO.output(red, GPIO.LOW)
    GPIO.output(yellow, GPIO.LOW)


blink()
