#!/usr/bin/env python3
# -*- coding: utf8 -*-
from enum import Enum, unique
import logging


@unique
class NfcEvent(Enum):
    DETECT = 1
    REMOVE = 2
    REDETECT = 3


def resolve(template: dict, event: NfcEvent):
    # logging.debug("Action " + event.name + " for tag " + tag_id)

    event_to_key_map = {
        NfcEvent.DETECT: "ondetect" if "ondetect" in template else "url",
        NfcEvent.REMOVE: "onremove",
        NfcEvent.REDETECT: "onredetect" if "onredetect" in template else "ondetect" if "ondetect" in template else "url"
    }

    event_key = event_to_key_map[event]

    if event_key not in template:
        return

    # configure list of actions
    if type(template[event_key]) is list:
        return template[event_key]
    # legacy: just one action
    elif type(template[event_key]) is dict:
        return [template[event_key]]
    # very legacy: just url
    else:
        return [{"type": "curl", "url": template[event_key]}]
