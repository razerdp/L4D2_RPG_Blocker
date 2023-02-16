# -*- coding: utf-8 -*-
# created by fengweichao on 2023/2/16
import os.path
import pathlib
import json

ENCODE = 'utf-8'

SETTINGS_FILE_PATH = './settings.settings'

SETTINGS = {}

if os.path.exists(SETTINGS_FILE_PATH):
    with open(SETTINGS_FILE_PATH, 'r', encoding=ENCODE) as f:
        s = f.read()
        if s:
            settings = json.loads(s)
            settings and SETTINGS.update(settings)
        f.close()


def SaveSettings(key, value):
    global SETTINGS
    SETTINGS[str(key)] = value
    with open(SETTINGS_FILE_PATH, 'w', encoding=ENCODE) as f:
        f.write(str(json.dumps(SETTINGS, ensure_ascii=False, indent=2)))
        f.close()


def GetSettings(key, default_value=None):
    global SETTINGS
    return SETTINGS.get(str(key), default_value)
