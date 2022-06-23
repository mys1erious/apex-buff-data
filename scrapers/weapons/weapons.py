from hashlib import new
from textwrap import indent
from bs4 import BeautifulSoup as bs
import requests
import json

# Create weapons dictionary
weapons = dict()

# Connect to Apex Wiki website
url = 'https://apexlegends.fandom.com/wiki/Weapon'
response = requests.get(url)

# Parsing through the website
doc = bs(response.content, 'html.parser')  # Main document
wikitable = doc.find('table', class_='wikitable')  # Weapons table
tbody = wikitable.find('tbody')  # Weapons table tbody
trs = tbody.find_all('tr')  # tbody tr

# The main loop for adding weapon's data to the dictionary
for i in range(2, len(trs)):
    tds = trs[i].find_all('td')
    weapon = tds[0].b.text.strip()
    weapon_img = tds[0].img['data-src']
    weapon_type = tds[1].text.strip()
    weapon_ammo = ' '.join([i.text for i in tds[2].find_all('a')]).split()
    weapon_ammo_img = ' '.join([i['data-src'] for i in tds[2].find_all('img')]).split()
    weapon_attachments = list(filter(None, [i.get('title') for i in tds[3].find_all('a')]))
    weapon_attachments_img = [i['data-src'] for i in tds[3].find_all('img')]
    mag_size = ' '.join([i.text for i in tds[4]]).split()
    rpm = ' '.join([i.text for i in tds[5]]).split()
    dps = ' '.join([i.text for i in tds[6]]).split()
    ttk = ' '.join([i.text for i in tds[7]]).split()
    projectile_speed = tds[8].text.strip()
    fire_modes = ' '.join([i['title'] for i in tds[9].find_all('a')]).split()
    fire_modes_img = [i['data-src'] for i in tds[9].find_all('img')]
    body_damage = tds[10].text.strip()
    head_damage = tds[11].text.strip()
    legs_damage = tds[12].text.strip()

    weapons[weapon] = {'weapon_img': weapon_img,
                       'weapon_type': weapon_type,
                       'weapon_ammo': weapon_ammo,
                       'weapon_ammo_img': weapon_ammo_img,
                       'weapon_attachments': weapon_attachments,
                       'weapon_attachments_img': weapon_attachments_img,
                       'mag_size': mag_size,
                       'rpm': rpm,
                       'dps': dps,
                       'ttk': ttk,
                       'projectile_speed': projectile_speed,
                       'fire_modes': fire_modes,
                       'fire_modes_img': fire_modes_img,
                       'body_damage': body_damage,
                       'head_damage': head_damage,
                       'legs_damage': legs_damage
                       }

# Write and save to JSON
with open('weapons.json', 'w') as outfile:
    json.dump(weapons, outfile, indent=2)