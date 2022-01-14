#!/usr/bin/env python3
# -*- coding: utf8 -*-

import requests
import time
import logging

def getVolumioStatus(baseUrl: str):
  try:
     response = requests.get(baseUrl + '/api/v1/getState', timeout=2)
     response.raise_for_status()
  except requests.exceptions.HTTPError as errHttp:
    logging.debug('Get Volumio state returned HTTP error: %s', errHttp)
    return
  except requests.ConnectionError as errCon:
    logging.debug('Get Volumio state http connection error: %s', errCon)
    return
  except requests.Timeout as errTimeout:
    logging.debug('Get Volumio state http timeout: %s', errTimeout)
    return
  except requests.exceptions.RequestException as errReq:
    logging.warning('Get Volumio state request Error: %s', errReq)
    return

  json_data = response.json()
  if ('status' not in json_data):
      logging.warning ('Get Volumio state: no Status in response')
      return

  return json_data['status']
  

def waitForVolumio(baseUrl: str):
  while True:
    volumioState = getVolumioStatus(baseUrl)
    if volumioState is not None:
      return
    time.sleep(2)