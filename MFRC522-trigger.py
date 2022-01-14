#!/usr/bin/env python3
# -*- coding: utf8 -*-

import pirc522
import sys
from os import path
import time
import csv
import json
import logging
import logging.config
import logging.handlers
import statusled
import volumiostatus
from actions import NfcEvent, execute_action
from config import validate_config

# welcome message
logging.info("Welcome to MFRC522-trigger!")
statusled.setRed()
logging.info("Press Ctrl-C to stop.")

# read config
pathname = path.dirname(path.abspath(__file__))
logging.config.fileConfig(pathname + '/logging.ini')
config = json.load(open(pathname + '/config.json', encoding="utf-8"))
validate_config(config)
templates = config['tag-templates']
volumio_config = config.get("volumio")

# build tags dictionary from tags.csv
tags = {} # tag : {param1, templateid}
with open(pathname + '/tags.csv', 'r', newline='') as file:
    tagscsv = csv.DictReader(file, dialect='unix')
    for row in tagscsv:
        templateid = row['template']
        if (templateid not in templates):
            logging.warning("Template '" + templateid + "' missing in tag-templates")
            continue
        action_template = templates[templateid]
        tags[row['tag']] = {'param1': row['param1'], 'templateid': templateid}
logging.info(tags)

# wait for volumio
if (volumio_config is not None):
    volumiostatus.waitForVolumio()
    time.sleep(volumio_config.get('startup-delay'))  # volumio API is ready before volumio is - so just wait a little longer
    logging.info("Volumio is ready")
else:
    logging.info("Volumio not configured")
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
            execute_action(tags, templates, NfcEvent.REMOVE, current_tag)
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
        execute_action(tags, templates, NfcEvent.REDETECT if current_tag == last_tag else NfcEvent.DETECT, tag_id)

        last_tag = current_tag
    except KeyboardInterrupt:
        logging.info("Shutdown!")
        break
    except Exception:
        logging.exception("Unexpected exception '%s' occurred!", str(sys.exc_info()[0].__name__))
        break
statusled.destroy()
reader.cleanup()
