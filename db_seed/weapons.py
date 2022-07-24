import requests
import logging

from constants import *
from utils.utils import load_json_data, slugify, print_dict_prettify


logging.basicConfig(
    level=logging.INFO,
    filename='weapon_responses.log',
    filemode='w'
)


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

    if not response.ok:
        logging.error(f'POST_{dep_type.upper() if dep_type else ""}_TO_WEAPON: {response}')

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


def get_fire_modes_data_from_weapon(weapon):
    init_data = {'fire_modes': []}
    fire_modes = weapon['weapon_fire_modes']
    rpm = weapon['rpm']
    dps = weapon['dps']
    ttk = weapon['ttk']
    # {
    #     "fire_mode_slug": "single",
    #     "modificator_slug": "default",
    #     "rpm": {"min": 10, "max": 20},
    #     "dps": {"min": 15, "max": 40},
    #     "ttk": {"min": 10, "max": 10}
    # }

    # Want to puke watching this implementation..., refactor later
    #   right now needed just for API testing
    for i, fire_mode in enumerate(fire_modes):
        if isinstance(rpm, list):
            try:
                cur_rpm = rpm[i]
                cur_dps = dps[i]
                cur_ttk = ttk[i]
                temp_rpm = {}
                temp_dps = {}
                temp_ttk = {}
                if isinstance(cur_rpm, dict):
                    temp_rpm = cur_rpm
                    temp_dps = cur_dps
                    temp_ttk = cur_ttk
                else:
                    temp_rpm['min'] = cur_rpm
                    temp_rpm['max'] = cur_rpm
                    temp_dps['min'] = cur_dps
                    temp_dps['max'] = cur_dps
                    temp_ttk['min'] = cur_ttk
                    temp_ttk['max'] = cur_ttk
            except KeyError:
                temp_rpm = None,
                temp_dps = None,
                temp_ttk = None

            init_data['fire_modes'].append(
                {
                    'fire_mode_slug': slugify(fire_mode),
                    'modificator_slug': 'default',
                    'rpm': temp_rpm,
                    'dps': temp_dps,
                    'ttk': temp_ttk
                }
            )
        else:
            init_data['fire_modes'].append(
                {
                    'fire_mode_slug': slugify(fire_mode),
                    'modificator_slug': 'default',
                    'rpm': rpm,
                    'dps': dps,
                    'ttk': ttk
                }
            )

    # print(json.dumps(init_data, indent=4))
    return init_data


def post_weapon(weapon, url):
    weapon_data = get_weapon_data_from_weapon(weapon)
    attachments_data = get_attachments_data_from_weapon(weapon)
    ammo_data = get_ammo_data_from_weapon(weapon)
    mag_data = get_mag_data_from_weapon(weapon)
    damage_data = get_damage_data_from_weapon(weapon)
    fire_modes_data = get_fire_modes_data_from_weapon(weapon)

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
    logging.info(f'--- POST_WEAPON `{weapon_name}`: {post_weapon_response}')
    if not post_weapon_response.ok:
        logging.error(f'--- POST_WEAPON `{weapon_name}`: {post_weapon_response}')
        try:
            logging.error(post_weapon_response.json()+'\n')
        except Exception:
            pass

    if post_weapon_response.ok:
        weapon_url = f'{url}{slugify(weapon_name)}/'

        put_ps_response = requests.put(
            url=weapon_url,
            json={'projectile_speed': projectile_speed},
            auth=ADMIN_CREDS
        )

        if not put_ps_response.ok:
            logging.error(f'PUT_PROJECTILE_SPEED `{weapon_name}`: {put_ps_response}')

        post_deps_to_weapon(attachments_data, weapon_url+'attachments/', 'attachments')
        post_deps_to_weapon(ammo_data, weapon_url+'ammo/', 'ammo')
        post_deps_to_weapon(mag_data, weapon_url+'mags/', 'mags')
        post_deps_to_weapon(damage_data, weapon_url + 'damage/', 'damage', json=True)

        post_deps_to_weapon(fire_modes_data, weapon_url + 'fire_modes/', 'fire_modes', json=True)


def post_weapons(weapons, url):
    for weapon in weapons:
        # weapon = weapons[9]
        post_weapon(weapon, url)
        break


def seed():
    url = LOCAL_BASE_API_URL
    weapons_data = load_json_data(WEAPONS_JSON)

    post_weapons(weapons_data, url=url+'/weapons/')


if __name__ == '__main__':
    ...
    seed()
