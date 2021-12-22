#!/usr/bin/env python3
# -*- coding: utf8 -*-

import pirc522
import sys
from os import path
import urllib.request
import subprocess
import time
import json
import logging
import logging.config
import logging.handlers

from actions import NfcEvent, resolve
from config import validate_config

pathname = path.dirname(path.abspath(__file__))
logging.config.fileConfig(pathname + '/logging.ini')
config = json.load(open(pathname + '/config.json', encoding="utf-8"))


def execute_curl(url):
    logging.info("Gonna curl '" + url + "'")
    try:
        urllib.request.urlopen(url)
    except Exception:
        logging.error("Unable to open url " + url, sys.exc_info()[0])


def execute_command(command):
    logging.info("Gonna execute '" + command + "'")
    subprocess.call(command, shell=True, stdout=subprocess.DEVNULL)


ACTION_MAP = {
    "curl": lambda action: execute_curl(action["url"]),
    "command": lambda action: execute_command(action["command"])
}


def execute_action(event: NfcEvent, tag_id: str):

    resolved_actions = resolve(config, event, tag_id)

    for action in resolved_actions:
        ACTION_MAP[action["type"]](action)


# welcome message
logging.info("Welcome to MFRC522-trigger!")
validate_config(config)
logging.info("Press Ctrl-C to stop.")

# create a reader
reader = pirc522.RFID(bus=1, pin_irq=31, pin_rst=29)

current_tag = ''
last_tag = ''
count = 0
polling = False

# This loop keeps checking for chips. If one is near it will get the UID and authenticate
while True:
    try:
        # wait for reader to send an interrupt
        if not polling:
            reader.wait_for_tag()

        count += 1
        logging.debug("Reader loop %d", count)

        # scan for cards
        if not polling:
            (error, tag_type) = reader.request()

            # on error continue and retry
            if error:
                # logging.info("error request")
                polling = False
                continue

        # get the UID of the card
        (error, uid) = reader.anticoll()

        # on error continue and retry
        if error:
            # logging.info("error anticoll")
            execute_action(NfcEvent.REMOVE, current_tag)
            current_tag = ''
            polling = False
            continue

        # transform UID into string representation
        tag_id = ''.join((str(x) for x in uid))

        polling = True

        # when we're still reading the same tag
        if current_tag == tag_id:
            # don't busy wait while there's a rfid tag near the reader
            time.sleep(0.1)
            continue

        current_tag = tag_id

        # execute an action for the reading tag
        execute_action(NfcEvent.REDETECT if current_tag == last_tag else NfcEvent.DETECT, tag_id)

        last_tag = current_tag
    except KeyboardInterrupt:
        logging.info("Shutdown!")
        break
    except Exception:
        logging.exception("Unexpected exception '%s' occurred!", str(sys.exc_info()[0].__name__))
        break

reader.cleanup()
