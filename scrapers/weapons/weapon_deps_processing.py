import json

from constants import *
from utils.utils import load_json_data, save_to_json, cut_to_end_pattern


def get_all_unique_vals(path, data, attr_name):
    map = {attr_name: []}
    for weapon in data['weapons']:
        for ind, name in enumerate(weapon[f'weapon_{attr_name}']):
            if name not in {obj['name'] for obj in map[attr_name]}:
                map[attr_name].append({
                    'name': name,
                    'img': weapon[f'weapon_{attr_name}_img'][ind]
                })

    save_to_json(path, map)
    return map


def get_all_unique_ammo_types(data):
    return get_all_unique_vals(f'weapon_ammo.json', data, 'ammo')


def get_all_unique_attachments(data):
    return get_all_unique_vals(f'weapon_attachments.json', data, 'attachments')


def get_all_unique_fire_modes(data):
    return get_all_unique_vals(f'weapon_fire_modes.json', data, 'fire_modes')


def setup():
    ...
    # data = load_json_data(WEAPONS_JSON)
    #
    # ammo = get_all_unique_ammo_types(data)
    # attachments = get_all_unique_attachments(data)
    # firemods = get_all_unique_fire_modes(data)


if __name__ == '__main__':
    setup()
