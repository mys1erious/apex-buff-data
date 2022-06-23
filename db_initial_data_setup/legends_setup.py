import requests
import json

from constants import *


def legends_data_from_file(file):
    with open(file, 'r') as f:
        data = json.load(f)

        return data


def post_legend(url, legend):
    response = requests.post(url + '/legends/', data=legend)
    return response


def post_legends(url, data):
    for i, legend in enumerate(data['legends']):
        response = post_legend(url, legend)

        if not response.ok:
            print(i, response.status_code, response.json())
        else:
            print(f'{i}. {legend.name}: Success')


def setup():
    url = HEROKU_DEV_BASE_API_URL  # Change this url depending on which base url u want to use
        # (later rework for auto data adding)
    data = legends_data_from_file(PATH_TO_LEGENDS_JSON)
    post_legends(url, data)
