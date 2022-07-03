import base64
import re

import requests
import json

from constants import *


def legends_data_from_file(file):
    with open(file, 'r') as f:
        data = json.load(f)

        return data


def put_legend_type(url, legend_type):
    response = requests.put(url, data=legend_type, auth=(ADMIN_USERNAME, ADMIN_PASSWORD))
    return response


def post_legend_ability(url, legend_ability, legend_name):
    legend_ability.pop('icon_url')

    ability_icon_fullname = f'{legend_name.replace(" ", "_").lower()}_{legend_ability["name"].replace(" ", "_").lower()}'
    ability_icon_path = f'{LEGEND_ABILITY_IMAGES_DIR}/{ability_icon_fullname}.png'

    # For now here
    cd_str = legend_ability.pop('cooldown')
    cd_pattern = r"[-+]?(?:\d*\.\d+|\d+)"

    cd = None
    if cd_str:
        cd = float(re.search(cd_pattern, cd_str).group(0))

    if 'minute' in cd_str:
        cd *= 60
    legend_ability['cooldown'] = cd

    with open(ability_icon_path, 'rb') as img:
        post_response = requests.post(
            url,
            data=legend_ability,
            files={'icon': img},
            auth=(ADMIN_USERNAME, ADMIN_PASSWORD)
        )

    return post_response


def post_legend_abilities(url, legend_abilities, legend_name):
    for ability in legend_abilities:
        post_legend_ability(url, ability, legend_name)


def post_legend(url, legend):
    legend_name = legend.get('name')
    legend.pop('icon_url')
    legend_icon_path = f'{LEGEND_IMAGES_DIR}/{legend_name}.png'

    legend_type = legend.pop('legend_type')
    legend_abilities = legend.pop('abilities')

    with open(legend_icon_path, 'rb') as img:
        post_response = requests.post(url, data=legend, files={'icon': img}, auth=(ADMIN_USERNAME, ADMIN_PASSWORD))

    if post_response.ok:
        legend_slug = legend['name'].lower().replace(' ', '-')

        put_legend_type_response = put_legend_type(url + f'{legend_slug}/type/', {'legend_type': legend_type})
        if not put_legend_type_response.ok:
            print(f'{legend["name"]}: ', put_legend_type_response.status_code, put_legend_type_response.json())

        post_legend_abilities(
            url + f'{legend_slug}/abilities/',
            legend_abilities,
            legend_name
        )

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

    data = legends_data_from_file(LEGENDS_JSON)

    post_legends(url + '/legends/', data)
    ...


if __name__ == '__main__':
    setup()


