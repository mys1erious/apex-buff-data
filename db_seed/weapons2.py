import json

import requests

from constants import *
from utils.utils import load_json_data, slugify, print_dict_prettify


def get_weapon_data_from_weapon(weapon):
    weapon_fields = ['weapon_name', 'weapon_type']
    data_fields = ['name', 'weapon_type']
    weapon_img_path = f'{WEAPON_IMAGES_DIR}/{weapon["weapon_name"]}.png'

    data = {
        'weapon_img_path': weapon_img_path
    }
    for weapon_field, data_field in zip(weapon_fields, data_fields):
        data[data_field] = weapon[weapon_field]

    return data


def get_attachments_data_from_weapon(weapon):
    attachments = weapon['weapon_attachments']
    data = {'attachments': []}

    for ind, attachment in enumerate(attachments):
        data['attachments'].append({'attachment_slug': slugify(attachment)})

    return data


def post_attachment_to_weapon(attachment: dict, url):
    response = requests.post(
                url=url,
                data=attachment,
                auth=ADMIN_CREDS
            )

    print(f'POST_ATTACHMENT_TO_WEAPON `{list(attachment.items())[0][1]}`: {response}')
    return response


def post_attachments_to_weapon(data: dict, url):
    for attachment in data['attachments']:
        post_attachment_to_weapon(attachment, url)


def post_weapon(weapon, url):
    weapon_data = get_weapon_data_from_weapon(weapon)
    attachments_data = get_attachments_data_from_weapon(weapon)

    weapon_name = weapon_data.get('name')
    weapon_img_path = weapon_data.pop('weapon_img_path')

    with open(weapon_img_path, 'rb') as img:
        post_weapon_response = requests.post(
            url=url,
            data=weapon_data,
            files={'icon': img},
            auth=ADMIN_CREDS
        )
    print(f'--- POST_WEAPON `{weapon_name}`: {post_weapon_response}')

    if post_weapon_response.ok:
        weapon_url = f'{url}{slugify(weapon_name)}'

        post_attachments_to_weapon(attachments_data, weapon_url+'/attachments/')


def post_weapons(weapons, url):
    for weapon in weapons:
        post_weapon(weapon, url)
        break


def seed():
    url = LOCAL_BASE_API_URL
    weapons_data = load_json_data(WEAPONS_JSON)

    post_weapons(weapons_data, url=url+'/weapons/')


if __name__ == '__main__':
    ...
    seed()
