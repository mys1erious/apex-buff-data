import json

from constants import *
from utils.utils import (
    load_json_data,
    save_to_json,
    cut_to_end_pattern,
    get_attrs_from_json
)


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


def preprocess_weapon_attack_stats(rpms, dpss, ttks, fire_modes):
    for rpm, dps, ttk, fire_mode in zip(rpms, dpss, ttks, fire_modes):
        if any(isinstance(var, dict) for var in [rpm, dps, ttk]):
            pass
        elif all(isinstance(var, list) for var in [rpm, dps, ttk]):
            if len(fire_mode) >= 2 and all(len(lst) < len(fire_mode) for lst in [rpm, dps, ttk]):
                [equalize_attack_stat_with_fire_mode(stat, fire_mode) for stat in [rpm, dps, ttk]]


def equalize_attack_stat_with_fire_mode(stat, fire_mode):
    for _ in range(len(fire_mode)-len(stat)):
        stat.append(stat[0])
    return stat


def preprocess_weapons(weapons):
    attack_stat_fields = get_attrs_from_json(weapons, ['rpm', 'dps', 'ttk', 'weapon_fire_modes'])
    rpms = attack_stat_fields['rpm']
    dpss = attack_stat_fields['dps']
    ttks = attack_stat_fields['ttk']
    fire_modes = attack_stat_fields['weapon_fire_modes']

    preprocess_weapon_attack_stats(rpms, dpss, ttks, fire_modes)

    save_to_json(WEAPONS_JSON, weapons)


def setup():
    ...
    data = load_json_data(WEAPONS_JSON)['weapons']
    preprocess_weapons(data)

    # ammo = get_all_unique_ammo_types(data)
    # attachments = get_all_unique_attachments(data)
    # firemods = get_all_unique_fire_modes(data)


if __name__ == '__main__':
    setup()
