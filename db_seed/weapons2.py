import json
import requests
from requests_toolbelt.utils import formdata
import cv2
import base64

from constants import *
from utils.utils import load_json_data, slugify, print_dict_prettify


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


# -- Attachments --
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


# -- Ammo --
def get_ammo_data_from_weapon(weapon):
    ammo = weapon['weapon_ammo']
    data = {'ammo': []}

    for ind, ammo_obj in enumerate(ammo):
        data['ammo'].append({'ammo_slug': slugify(ammo_obj)})

    return data


def post_ammo_to_weapon(ammo: dict, url):
    response = requests.post(
                url=url,
                data=ammo,
                auth=ADMIN_CREDS
            )

    print(f'POST_AMMO_TO_WEAPON `{list(ammo.items())[0][1]}`: {response}')
    return response


def post_ammo_list_to_weapon(data: dict, url):
    for ammo in data['ammo']:
        post_ammo_to_weapon(ammo, url)


# -- Mag --
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


def post_mag_to_weapon(mag, url):
    response = requests.post(
        url=url,
        data=mag,
        auth=ADMIN_CREDS
    )
    print(f'POST_MAG_TO_WEAPON `{list(mag.items())[0][1]}`: {response}')
    return response


def post_mags_to_weapon(data, url):
    for mag in data['mags']:
        post_mag_to_weapon(mag, url)


def post_weapon(weapon, url):
    weapon_data = get_weapon_data_from_weapon(weapon)
    attachments_data = get_attachments_data_from_weapon(weapon)
    ammo_data = get_ammo_data_from_weapon(weapon)
    mag_data = get_mag_data_from_weapon(weapon)

    # print(weapon_data)
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
        #print(put_ps_response.json())

        post_attachments_to_weapon(attachments_data, weapon_url+'attachments/')
        post_ammo_list_to_weapon(ammo_data, weapon_url+'ammo/')
        post_mags_to_weapon(mag_data, weapon_url+'mags/')


def post_weapons(weapons, url):
    for weapon in weapons:
        weapon = weapons[1]
        post_weapon(weapon, url)
        break


def seed():
    url = LOCAL_BASE_API_URL
    weapons_data = load_json_data(WEAPONS_JSON)

    post_weapons(weapons_data, url=url+'/weapons/')


if __name__ == '__main__':
    ...
    seed()
