#!/usr/bin/env python3
# -*- coding: utf8 -*-

import RPi.GPIO as GPIO

redLedPin   = 37
greenLedPin = 29
blueLedPin  = 31

def setup():
  GPIO.setmode(GPIO.BOARD)
  GPIO.setup(redLedPin,GPIO.OUT)
  GPIO.setup(greenLedPin,GPIO.OUT)
  GPIO.setup(blueLedPin,GPIO.OUT)
  setRgb(True, False, False) # initially RED

def setRgb(red, green, blue):
  GPIO.output(redLedPin, GPIO.HIGH if red else GPIO.LOW)
  GPIO.output(greenLedPin, GPIO.HIGH if green else GPIO.LOW)
  GPIO.output(blueLedPin, GPIO.HIGH if blue else GPIO.LOW)
  
def destroy():
  setRgb(False, False, False)    ## LED off
  GPIO.cleanup()                 ## Release resource
