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
        NfcEvent.DETECT: "ondetect",
        NfcEvent.REMOVE: "onremove",
        NfcEvent.REDETECT: "onredetect" if "onredetect" in template else "ondetect"
    }

    event_key = event_to_key_map[event]

    if event_key not in template:
        return

    return template[event_key]