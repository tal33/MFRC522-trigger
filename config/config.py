#!/usr/bin/env python3
# -*- coding: utf8 -*-

import json
from os import path
import logging
from fastjsonschema import validate, JsonSchemaException


def validate_config(config: object):
    with open(path.dirname(path.abspath(__file__)) + '/config.schema.json', encoding="utf-8") as file:
        schema = json.load(file)

    try:
        validate(schema, config)
        return True
    except JsonSchemaException as e:
        logging.warning("Your config is invalid: %s!", e)
        logging.warning("Please update your configuration file according to https://github.com/tal33/MFRC522-trigger#json-schema.")
        return False
