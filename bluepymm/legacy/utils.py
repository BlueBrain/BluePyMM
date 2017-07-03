import os
import json


def load_json(file_name):
    with open(file_name) as f:
        return json.load(f)


def makedirs(path):
    try:
        os.makedirs(path)
    except OSError:
        pass
    return path
