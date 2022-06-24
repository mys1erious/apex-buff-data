import requests
import json

from constants import *


def legends_data_from_file(file):
    with open(file, 'r') as f:
        data = json.load(f)

        return data


def put_legend_type(url, legend_type):
    response = requests.put(url, data=legend_type)
    return response


def post_legend(url, legend):
    legend_type = legend.pop('legend_type')
    post_response = requests.post(url, data=legend)

    if post_response.ok:
        legend_slug = legend['name'].lower().replace(' ', '-')
        put_response = put_legend_type(url + f'{legend_slug}/type/', {'legend_type': legend_type})

        if not put_response.ok:
            print(f'{legend["name"]}: ', put_response.status_code, put_response.json())

    return post_response


def post_legends(url, data):
    for i, legend in enumerate(data['legends']):
        response = post_legend(url, legend)

        if not response.ok:
            print(i, response.status_code, response.json())
        else:
            print(f'{i}. {legend["name"]}: Success')


def setup():
    url = LOCAL_BASE_API_URL  # Change this url depending on which base url u want to use
        # (later rework for auto data adding)

    data = legends_data_from_file(PATH_TO_LEGENDS_JSON)

    post_legends(url + '/legends/', data)

