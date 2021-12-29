#!/usr/bin/env python3
# -*- coding: utf8 -*-

import RPi.GPIO as GPIO

redLedPin   = 8   # also TXD with enable_uart so that this is turned on as early as possible
greenLedPin = 29
blueLedPin  = 0   # we ignore blue

def setup():
  GPIO.setmode(GPIO.BOARD)
  if redLedPin > 0: GPIO.setup(redLedPin,GPIO.OUT)
  if greenLedPin > 0: GPIO.setup(greenLedPin,GPIO.OUT)
  if blueLedPin > 0: GPIO.setup(blueLedPin,GPIO.OUT) 
  setRed() # initially RED, also because of using same GPIO as UART

def setRgb(red: bool, green: bool, blue: bool):
  if redLedPin > 0: GPIO.output(redLedPin, GPIO.HIGH if red else GPIO.LOW)
  if greenLedPin > 0: GPIO.output(greenLedPin, GPIO.HIGH if green else GPIO.LOW)
  if blueLedPin > 0: GPIO.output(blueLedPin, GPIO.HIGH if blue else GPIO.LOW)

def setRed():
  setRgb(True, False, False)

def setGreen():
  setRgb(False, True, False)

def setYellow():
  setRgb(True, True, False)

def setBlue():
  setRgb(False, False, True)

def setWhite():
  setRgb(True, True, True)

def destroy():
  setRed()    ## red again until powered off
  GPIO.cleanup()                 ## Release resource
