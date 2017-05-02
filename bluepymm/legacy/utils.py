import os
import csv
import json


def load_csv_to_dict(file_name):
    with open(file_name) as f:
        reader = csv.DictReader(f)
        ret = {row['combo_name']: row for row in reader}
    return ret


def load_json(file_name):
    with open(file_name) as f:
        return json.load(f)


def makedirs(path):
    try:
        os.makedirs(path)
    except OSError:
        pass
    return path
