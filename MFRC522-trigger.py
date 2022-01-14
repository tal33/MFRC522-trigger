#!/usr/bin/env python3
# -*- coding: utf8 -*-

import pirc522
import sys
from os import path
import urllib.request
import subprocess
import time
import csv
import json
import logging
import logging.config
import logging.handlers

import statusled
import volumiostatus
from actions import NfcEvent, resolve
from config import validate_config

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
    "curl": lambda action, code: execute_curl(action["url"].replace("<CODE>", code)),
    "command": lambda action, code: execute_command(action["command"].replace("<CODE>", code))
}


def execute_action(event: NfcEvent, tag_id: str):
    # get tag definition
    if tag_id not in tags:
        logging.warning("No mapping for tag " + tag_id)
        return
    tagdef = tags[tag_id]
    tag_code = tagdef['code']
    template_id = tagdef['templateid']
    if (template_id not in templates):
        logging.warning("Unknown actions-template " + template_id)
        return
    template = templates[template_id]
    template_name = template['name'].replace("<CODE>", tag_code)
    # get action from template
    resolved_actions = resolve(template, event)
    if (resolved_actions is None):
        logging.debug("No action for event " + event.name +" for tag " + tag_id + " in template " + template_name + " with id " + template_id)
        return
    # execute actions from template
    logging.info("Executing '" + template_name + " for " + event.name)
    for action in resolved_actions:
        ACTION_MAP[action["type"]](action, tag_code)

# welcome message
logging.info("Welcome to MFRC522-trigger!")
statusled.setRed()
logging.info("Press Ctrl-C to stop.")

# read configs
pathname = path.dirname(path.abspath(__file__))
logging.config.fileConfig(pathname + '/logging.ini')
config = json.load(open(pathname + '/config.json', encoding="utf-8"))
validate_config(config)

templates = config['tag-templates']
tags = {} # tag : {code, templateid}
with open(pathname + '/tags.csv', 'r', newline='') as file:
    tagscsv = csv.DictReader(file, dialect='unix')
    for row in tagscsv:
        action_template = templates[row['template']]
        tags[row['tag']] = {'code': row['code'], 'templateid': row['template']}
        print (tags[row['tag']])
print (tags)

# wait for volumio
volumiostatus.waitForVolumio()
time.sleep(5)   # volumio API is ready before volumio is - so just wait a little longer
logging.info("Volumio is ready")
statusled.setGreen()

# create a reader
reader = pirc522.RFID()

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
            statusled.setGreen()
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

        statusled.setYellow()
        # execute an action for the reading tag
        execute_action(NfcEvent.REDETECT if current_tag == last_tag else NfcEvent.DETECT, tag_id)

        last_tag = current_tag
    except KeyboardInterrupt:
        logging.info("Shutdown!")
        break
    except Exception:
        logging.exception("Unexpected exception '%s' occurred!", str(sys.exc_info()[0].__name__))
        break
statusled.destroy()
reader.cleanup()
