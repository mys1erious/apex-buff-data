import requests
import json

from bs4 import BeautifulSoup as bs
from selenium import webdriver

from constants import *
from utils.utils import save_to_json, cut_to_end_pattern


INFINITY_SYMBOL = '\u221e'

TABLE_FIELDS_MAP = {
    'weapon': 0,
    'type': 1,
    'ammo': 2,
    'attachments': 3,
    'mag_size': 4,
    'rpm': 5,
    'dps': 6,
    'ttk': 7,
    'projectile_speed': 8,
    'fire_modes': 9,
    'body_damage': 10,
    'head_damage': 11,
    'legs_damage': 12
}

SPECIAL_CASES_MAP = {
    'Heavy Rounds Revved Up': 'heavy_rounds_revved_up',
    'Double Tap Trigger': 'double_tap_trigger',
    'Amped': 'amped',
    'Modded Loader': 'modded_loader'
}


def weapon_dict(**kwargs):
    fields = [
        'weapon_name', 'weapon_img', 'weapon_type',
        'weapon_ammo', 'weapon_ammo_img',
        'weapon_attachments', 'weapon_attachments_img',
        'mag_size', 'rpm', 'dps', 'ttk', 'projectile_speed',
        'weapon_fire_modes', 'weapon_fire_modes_img',
        'body_damage', 'head_damage', 'legs_damage'
    ]

    weapon = {}
    for field in fields:
        try:
            weapon[field] = kwargs[field]
        except KeyError:
            pass

    return weapon


def parse_img(img):
    full_url = img['data-src']
    url = cut_to_end_pattern(full_url, ['.svg', '.png'])

    return url


def parse_weapon_field(field):
    weapon_name = field.b.text
    weapon_img = parse_img(field.find('img'))
    return weapon_name, weapon_img


def parse_ammo_field(field):
    str_field = str(field)

    ammo = [ammo.text.strip() for ammo in field.find_all('a', class_='mw-redirect')]
    ammo_img = [parse_img(ammo_img) for ammo_img in field.find_all('img')]

    # Cringy table has no 'mw-redirect' class in ammo field for Devotion, so hard-coded fix is required...
    #   as there are no other cases like this, the following solution will suffice
    if 'mw-redirect' not in str_field:
        ammo = [field.text[:-1].strip()]

    return ammo, ammo_img


def parse_attachments_field(attachments_field):
    attachments = [
        attachment.get('title')
        for attachment in attachments_field.find_all(
            'a',
            class_=lambda c: c != 'image'
        )
    ]
    attachments_img = [
        parse_img(attachment_img)
        for attachment_img in attachments_field.find_all(
            'img',
            alt=lambda a: 'Spacing.png' not in a
        )
    ]
    return attachments, attachments_img


def parse_mag_size_field(field):
    str_field = str(field)

    mag_size = {
        'normal': ''
    }

    if INFINITY_SYMBOL in str_field:
        mag_size['normal'] = -1
        return mag_size

    mag_sizes = [int(s) for s in field.text.split() if s.isdigit()]
    mag_size['normal'] = mag_sizes[0]

    for name, slug in SPECIAL_CASES_MAP.items():
        if name in str_field:
            mag_size[slug] = mag_sizes[1]

    return mag_size


def split_range_field_val(text, sep):
    vals = text.split(sep)
    return {
        'min': vals[0],
        'max': vals[1]
    }


def parse_attack_field(field):
    str_field = str(field)
    text = field.text
    stat = {}

    separators = ['~', '-']

    for sep in separators:
        if sep in text:
            return split_range_field_val(field.text, sep)

    # Not scaled for 2+ special cases(not required)
    for name, slug in SPECIAL_CASES_MAP.items():
        if name in str_field:
            vals = field.text.split()
            stat['normal'] = float(vals[0])
            stat[slug] = float(vals[1])
            return stat

    stat = [float(val) for val in field.text.split()]
    return stat


def parse_projectile_speed_field(field):
    text = field.text.strip()

    if 'Hitscan' in text:
        return 0

    sep = '-'
    if sep in text:
        return split_range_field_val(text, sep)
    return int(text)


def parse_fire_modes_field(field):
    fire_modes = [fire_mode['title'].strip() for fire_mode in field.find_all('a')]
    fire_mode_img = [parse_img(img) for img in field.find_all('img')]
    return fire_modes, fire_mode_img


def parse_damage_field(field):
    if '×' in field.text:
        field.small.extract()

    text = field.text.strip()
    str_field = str(field)

    sep = '-'
    if sep in text:
        return split_range_field_val(text, sep)

    dmg = {}
    for name, slug in SPECIAL_CASES_MAP.items():
        if name in str_field:
            vals = text.split()
            dmg['normal'] = float(vals[0])
            dmg[slug] = float(vals[1])
            return dmg

    return int(text)


def parse_weapon_fields_data(fields):
    weapon_name, weapon_img = parse_weapon_field(fields[TABLE_FIELDS_MAP['weapon']])
    weapon_type = fields[TABLE_FIELDS_MAP['type']].text

    ammo, ammo_img = parse_ammo_field(fields[TABLE_FIELDS_MAP['ammo']])
    attachments, attachment_imgs = parse_attachments_field(fields[TABLE_FIELDS_MAP['attachments']])

    mag_size = parse_mag_size_field(fields[TABLE_FIELDS_MAP['mag_size']])

    rpm = parse_attack_field(fields[TABLE_FIELDS_MAP['rpm']])
    dps = parse_attack_field(fields[TABLE_FIELDS_MAP['dps']])
    ttk = parse_attack_field(fields[TABLE_FIELDS_MAP['ttk']])
    projectile_speed = parse_projectile_speed_field(fields[TABLE_FIELDS_MAP['projectile_speed']])

    fire_modes, fire_mode_imgs = parse_fire_modes_field(fields[TABLE_FIELDS_MAP['fire_modes']])

    body_dmg = parse_damage_field(fields[TABLE_FIELDS_MAP['body_damage']])
    head_dmg = parse_damage_field(fields[TABLE_FIELDS_MAP['head_damage']])
    legs_dmg = parse_damage_field(fields[TABLE_FIELDS_MAP['legs_damage']])

    weapon = weapon_dict(
        weapon_name=weapon_name,
        weapon_img=weapon_img,
        weapon_type=weapon_type,
        weapon_ammo=ammo,
        weapon_ammo_img=ammo_img,
        weapon_attachments=attachments,
        weapon_attachments_img=attachment_imgs,
        mag_size=mag_size,
        rpm=rpm,
        dps=dps,
        ttk=ttk,
        projectile_speed=projectile_speed,
        weapon_fire_modes=fire_modes,
        weapon_fire_modes_img=fire_mode_imgs,
        body_damage=body_dmg,
        head_damage=head_dmg,
        legs_damage=legs_dmg,
    )

    return weapon

    #     body_damage = tds[10].text.strip()
    #     head_damage = tds[11].text.strip()
    #     legs_damage = tds[12].text.strip()


def scrape():
    # Create weapons dictionary
    weapons = {'weapons': []}

    # Connect to Apex Wiki website
    url = 'https://apexlegends.fandom.com/wiki/Weapon'
    response = requests.get(url)

    # Parsing through the website
    doc = bs(response.content, 'html.parser')  # Main document
    wikitable = doc.find('table', class_='wikitable')  # Weapons table
    tbody = wikitable.find('tbody')  # Weapons table tbody
    weapon_rows = tbody.find_all('tr')[2:]  # tbody tr

    # The main loop for adding weapon's data to the dictionary
    for row in weapon_rows:
        # row = weapon_rows[8]
        fields = row.find_all('td')
        weapon = parse_weapon_fields_data(fields)
        weapons['weapons'].append(weapon)

    save_to_json('weapons.json', weapons)


def get_dep_names_and_links(file, obj_type, field_name, field_img):
    names = []
    links = []
    with open(file, 'r') as f:
        data = json.load(f)
        for obj in data[obj_type]:
            names.append(obj[field_name])
            links.append(obj[field_img])
    return names, links


def download_images(save_path, names, links, prefix=''):
    browser = webdriver.Firefox()

    for i in range(len(names)):
        full_name = names[i]

        if isinstance(prefix, list) and len(prefix) == len(names):
            full_name = f'{prefix[i]}_{names[i]}'
            full_name = full_name.replace(' ', '_').lower()

        browser.get(links[i])
        browser.save_screenshot(f'{save_path}/{full_name}.png')

    browser.quit()


def download_weapon_dep_images(ammo=True, attachments=True, firemods=True):
    if ammo:
        names, links = get_dep_names_and_links(
            os.path.join(WEAPONS_DIR, 'weapon_ammo.json'),
            'ammo',
            'name',
            'img'
        )
        download_images(
            WEAPON_AMMO_IMAGES_DIR,
            names,
            links
        )

    if attachments:
        names, links = get_dep_names_and_links(
            os.path.join(WEAPONS_DIR, 'weapon_attachments.json'),
            'attachments',
            'name',
            'img'
        )
        download_images(
            WEAPON_ATTACHMENT_IMAGES_DIR,
            names,
            links
        )

    if firemods:
        names, links = get_dep_names_and_links(
            os.path.join(WEAPONS_DIR, 'weapon_firemods.json'),
            'firemods',
            'name',
            'img'
        )
        download_images(
            WEAPON_FIREMODE_IMAGES_DIR,
            names,
            links
        )


def get_weapon_names_and_links(file):
    names = []
    links = []
    with open(file, 'r') as f:
        data = json.load(f)
        for name in data:
            names.append(name)
            links.append(data[name]['weapon_img'])
    return names, links


def download_weapon_images():
    names, links = get_weapon_names_and_links(WEAPONS_JSON)
    download_images(WEAPON_IMAGES_DIR, names, links)


if __name__ == '__main__':
    scrape()

    # download_weapon_dep_images(ammo=False, attachments=False, firemods=False)
    # download_weapon_images()
