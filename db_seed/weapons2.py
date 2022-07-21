import json
import requests
from requests_toolbelt.utils import formdata
import cv2
import base64

from constants import *
from utils.utils import load_json_data, slugify, print_dict_prettify


def post_dep_to_weapon(data: dict, url, json, dep_type=None):
    if json:
        response = requests.post(
            url=url,
            json=data,
            auth=ADMIN_CREDS
        )
    else:
        response = requests.post(
                    url=url,
                    data=data,
                    auth=ADMIN_CREDS
                )

    print(f'POST_{dep_type if dep_type else ""}_TO_WEAPON: {response}')
    return response


def post_deps_to_weapon(data: dict, url, dep_type, json=False):
    for item in data[dep_type]:
        post_dep_to_weapon(item, url, dep_type=dep_type, json=json)


def get_weapon_data_from_weapon(weapon):
    weapon_api_fields_map = {
        'weapon_name': 'name',
        'weapon_type': 'weapon_type',
        'projectile_speed': 'projectile_speed'
    }
    weapon_img_path = f'{WEAPON_IMAGES_DIR}/{weapon["weapon_name"]}.png'

    data = {
        'weapon_img_path': weapon_img_path
    }
    for key, val in weapon_api_fields_map.items():
        data[val] = weapon[key]

    try:
        data['projectile_speed']['name'] = 'projectile speed'
    except TypeError:
        projectile_speed = data['projectile_speed']
        data['projectile_speed'] = {
            'name': 'projectile speed',
            'min': projectile_speed,
            'max': projectile_speed
        }

    return data


def get_attachments_data_from_weapon(weapon):
    attachments = weapon['weapon_attachments']
    data = {'attachments': []}

    for ind, attachment in enumerate(attachments):
        data['attachments'].append({'attachment_slug': slugify(attachment)})

    return data


def get_ammo_data_from_weapon(weapon):
    ammo = weapon['weapon_ammo']
    data = {'ammo': []}

    for ind, ammo_obj in enumerate(ammo):
        data['ammo'].append({'ammo_slug': slugify(ammo_obj)})

    return data


def get_mag_data_from_weapon(weapon):
    mags = weapon['mag_size']

    data = {'mags': []}

    for key in mags:
        name = key
        if key == 'normal': name = 'default'
        data['mags'].append({
            'modificator_slug': slugify(name),
            'size': mags[key]
        })

    return data


def get_damage_data_from_weapon(weapon):
    init_data = {
        'body': weapon['body_damage'],
        'head': weapon['head_damage'],
        'legs': weapon['legs_damage']
    }
    data = {'damage': []}

    # Later (maybe) scale for different types (normal/amped)
    temp = {'modificator_slug': 'default'}
    for key, val in init_data.items():
        if key == 'body' or key == 'head' or key == 'legs':
            if isinstance(val, dict):
                temp2 = {}
                for key2, val2 in val.items():
                    temp2[key2] = val2
                temp[key] = temp2
            else:
                temp[key] = {'min': val, 'max': val}
    data['damage'].append(temp)

    return data


def post_weapon(weapon, url):
    weapon_data = get_weapon_data_from_weapon(weapon)
    attachments_data = get_attachments_data_from_weapon(weapon)
    ammo_data = get_ammo_data_from_weapon(weapon)
    mag_data = get_mag_data_from_weapon(weapon)
    damage_data = get_damage_data_from_weapon(weapon)

    # print(damage_data)
    # return

    weapon_name = weapon_data.get('name')
    weapon_img_path = weapon_data.pop('weapon_img_path')

    projectile_speed = weapon_data.pop('projectile_speed')

    with open(weapon_img_path, 'rb') as img:
        post_weapon_response = requests.post(
            url=url,
            data=weapon_data,
            files={'icon': img},
            auth=ADMIN_CREDS
        )
    print(f'--- POST_WEAPON `{weapon_name}`: {post_weapon_response}')
    if not post_weapon_response.ok:
        try:
            print(post_weapon_response.json())
        except Exception:
            pass

    if post_weapon_response.ok:
        weapon_url = f'{url}{slugify(weapon_name)}/'

        put_ps_response = requests.put(
            url=weapon_url,
            json={'projectile_speed': projectile_speed},
            auth=ADMIN_CREDS
        )
        print(f'PUT_PROJECTILE_SPEED `{weapon_name}`: {put_ps_response}')

        post_deps_to_weapon(attachments_data, weapon_url+'attachments/', 'attachments')
        post_deps_to_weapon(ammo_data, weapon_url+'ammo/', 'ammo')
        post_deps_to_weapon(mag_data, weapon_url+'mags/', 'mags')
        post_deps_to_weapon(damage_data, weapon_url + 'damage/', 'damage', json=True)


def post_weapons(weapons, url):
    for weapon in weapons:
        weapon = weapons[17]
        post_weapon(weapon, url)
        break


def seed():
    url = LOCAL_BASE_API_URL
    weapons_data = load_json_data(WEAPONS_JSON)

    post_weapons(weapons_data, url=url+'/weapons/')


if __name__ == '__main__':
    ...
    seed()
