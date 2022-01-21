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

# check if INTERNAL music library exists and contains any content
# this is to indicate a strange bug where the library is temporarely missing after startup
# returns True if internal library is present, False if missing, None if request failed
def isVolumioInternalLibraryPresent(baseUrl: str):
  try:
     response = requests.get(baseUrl + '/api/v1/browse?uri=music-library/INTERNAL&limit=2', timeout=3)
     response.raise_for_status()
  except requests.exceptions.HTTPError as errHttp:
    logging.debug('Get Volumio music-library/INTERNAL returned HTTP error: %s', errHttp)
    return
  except requests.ConnectionError as errCon:
    logging.debug('Get Volumio music-library/INTERNAL http connection error: %s', errCon)
    return
  except requests.Timeout as errTimeout:
    logging.debug('Get Volumio music-library/INTERNAL http timeout: %s', errTimeout)
    return
  except requests.exceptions.RequestException as errReq:
    logging.warning('Get Volumio music-library/INTERNAL request Error: %s', errReq)
    return

  try:
    json_data = response.json()
    listcount = json_data['navigation']['lists'][0]["count"]
    return listcount > 0
  except:
    logging.error('Get Volumio music-library/INTERNAL unexpected result')
    return

