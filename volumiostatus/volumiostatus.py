#!/usr/bin/env python3
# -*- coding: utf8 -*-

import requests
import time

def getVolumioStatus():
  try:
     response = requests.get('http://localhost:3000/api/v1/getState', timeout=2)
     response.raise_for_status()
  except requests.exceptions.HTTPError as errHttp:
    print('HTTP error: %s', errHttp)
    return False
  except requests.ConnectionError as errCon:
    print('Connection error: %s', errCon)
    return False
  except requests.Timeout as errTimeout:
    print('Timeout: %s', errTimeout)
    return False
  except requests.exceptions.RequestException as errReq:
    print('Request Error: %s', errReq)
    return False

  json_data = response.json()
  if ('status' not in json_data):
      print ('No Status returned')
      return False

  status= json_data['status']
  print (status)
  return True
  

def waitForVolumio():
  while True:
    volumioReady = getVolumioStatus()
    if volumioReady:
      break
    else:
      time.sleep(2)