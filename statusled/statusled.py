#!/usr/bin/env python3
# -*- coding: utf8 -*-

import RPi.GPIO as GPIO
from enum import Enum, unique, auto

class RgbColor(Enum):
  NONE = auto()
  RED = auto()
  BLUE = auto()
  GREEN = auto()
  YELLOW = auto()
  WHITE = auto()

statusled_initialized = False

redLedPin   = 8   # also TXD with enable_uart so that this is turned on as early as possible
greenLedPin = 29
blueLedPin  = 0   # we ignore blue

def setup():
  global statusled_initialized
  GPIO.setmode(GPIO.BOARD)
  if redLedPin > 0: GPIO.setup(redLedPin,GPIO.OUT)
  if greenLedPin > 0: GPIO.setup(greenLedPin,GPIO.OUT)
  if blueLedPin > 0: GPIO.setup(blueLedPin,GPIO.OUT) 
  statusled_initialized = True

def setRgb(red: bool, green: bool, blue: bool):
  if (not statusled_initialized): setup()
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


def setColor(color: RgbColor):
  if (color == RgbColor.NONE):
    return
  
  if (color == RgbColor.RED):
    setRed()
  elif (color == RgbColor.GREEN):
    setGreen()
  elif (color == RgbColor.BLUE):
    setBlue()
  elif (color == RgbColor.YELLOW):
    setYellow()
  elif (color == RgbColor.WHITE):
    setWhite()

def destroy():
  setRed()    ## red again until powered off
  statusled_initialized = False
  GPIO.cleanup()                 ## Release resource

def main():
  setup()
  setColor(RgbColor['green'.upper()])
  destroy()

if __name__ == '__main__':       ## Program start from here
    main()