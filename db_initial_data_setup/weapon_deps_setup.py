import requests

from constants import *
from utils.utils import load_json_data, slugify


def post_ammo_type(url, data):
    data.pop('img')
    data['name'] = data['name'].title()
    img_path = f'{WEAPON_AMMO_IMAGES_DIR}/{data["name"].title()}.png'

    with open(img_path, 'rb') as img:
        response = requests.post(
            url=url,
            data=data,
            files={'icon': img},
            auth=(ADMIN_USERNAME, ADMIN_PASSWORD)
        )
        if not response.ok:
            print(data['name'], response)


def post_ammo_types(url, data):
    for item in data['ammo']:
        item['name'] = item['name'].lower()
        post_ammo_type(url, data=item)


def post_attachment(url, data):
    data.pop('img')
    img_path = f'{WEAPON_ATTACHMENT_IMAGES_DIR}/{data["name"]}.png'

    with open(img_path, 'rb') as img:
        response = requests.post(
            url=url,
            data=data,
            files={'icon': img},
            auth=(ADMIN_USERNAME, ADMIN_PASSWORD)
        )
        if not response.ok:
            print(data['name'], response.json)


def post_attachments(url, data):
    for item in data['attachments']:
        post_attachment(url, data=item)


def post_fire_mode(url, data):
    data.pop('img')
    img_path = f'{WEAPON_FIREMODE_IMAGES_DIR}/{data["name"]}.png'

    with open(img_path, 'rb') as img:
        response = requests.post(
            url=url,
            data=data,
            files={'icon': img},
            auth=(ADMIN_USERNAME, ADMIN_PASSWORD)
        )
        if not response.ok:
            print(data['name'], response)


def post_fire_modes(url, data):
    for item in data['firemods']:
        post_fire_mode(url, data=item)


def dummy_special_data():
    data = {'specials': []}

    svg = '.svg'
    png = '.png'
    names_format_map = {
        'Heavy Rounds Revved Up': png,
        'Double Tap Trigger': svg,
        'Sniper Ammo Amped': png,
        'Modded Loader': svg
    }
    img_paths = [f'{WEAPON_SPECIALS_IMAGES_DIR}/{name}{f}' for name, f in names_format_map.items()]

    for i, name in enumerate(names_format_map.keys()):
        specials = data['specials']
        specials.append({
            'name': name,
            'img': img_paths[i]
        })

    return data


def post_special(url, special):
    img_path = ...

    with open(img_path, 'rb') as img:
        response = requests.post(
            url=url,
            data=data,
            files={'icon': img},
            auth=(ADMIN_USERNAME, ADMIN_PASSWORD)
        )
        if not response.ok:
            print(data['name'], response)

def post_specials(url, data):
    data = dummy_special_data()
    for item in data['specials']:
        post_special(url, item)


def setup(run=False):
    if run:
        url = LOCAL_BASE_API_URL
        weapons_data = load_json_data(WEAPONS_JSON)

        print(dummy_special_data())
        # post_attachments(
        #     url+'/attachments/',
        #     load_json_data(WEAPONS_DIR + '/weapon_attachments.json')
        # )
        # post_ammo_types(
        #     url+'/ammo/', load_json_data(WEAPONS_DIR+'/weapon_ammo.json')
        # )
        # post_fire_modes(
        #     url+'/fire_modes/',
        #     load_json_data(WEAPONS_DIR + '/weapon_fire_modes.json')
        # )
    else:
        raise ValueError('`run` is False.')


if __name__ == '__main__':
    setup(run=True)
