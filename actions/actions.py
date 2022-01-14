#!/usr/bin/env python3
# -*- coding: utf8 -*-
from enum import Enum, unique
import logging
import sys
import urllib.request
import subprocess


@unique
class NfcEvent(Enum):
    DETECT = 1
    REMOVE = 2
    REDETECT = 3

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
    "curl": lambda action, param1: execute_curl(action["url"].replace("<param1>", param1)),
    "command": lambda action, param1: execute_command(action["command"].replace("<param1>", param1))
}

def get_eventaction_from_template(template: dict, event: NfcEvent):
    event_to_key_map = {
        NfcEvent.DETECT: "ondetect",
        NfcEvent.REMOVE: "onremove",
        NfcEvent.REDETECT: "onredetect" if "onredetect" in template else "ondetect"
    }

    event_key = event_to_key_map[event]

    if event_key not in template:
        return

    return template[event_key]

# exported main function
def execute_action(tags: dict, templates: dict, event: NfcEvent, tag_id: str):
    # get tag definition
    if tag_id not in tags:
        logging.warning("No mapping for tag " + tag_id)
        return
    tagdef = tags[tag_id]
    tag_param1 = tagdef['param1']
    template_id = tagdef['templateid']
    if (template_id not in templates):
        logging.warning("Unknown template " + template_id)
        return
    template = templates[template_id]
    template_name = template['name'].replace("<param1>", tag_param1)

    # get action from template
    event_actions = get_eventaction_from_template(template, event)
    if (event_actions is None):
        logging.debug("No action for event " + event.name +" for tag " + tag_id + " in template " + template_name + " with id " + template_id)
        return

    # execute actions from template
    logging.info("Executing '" + template_name + " for " + event.name)
    for action in event_actions:
        ACTION_MAP[action["type"]](action, tag_param1)