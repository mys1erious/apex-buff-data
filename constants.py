import os
from pathlib import Path


# Base
BASE_DIR = Path(__file__).resolve().parent

LOCAL_BASE_API_URL = 'http://localhost:8000/api/v1'
HEROKU_DEV_BASE_API_URL = 'https://apex-buff-development.herokuapp.com/api/v1'

MAX_WAIT = 10
PAUSE = 0.3


# Legends
LEGENDS_DIR = os.path.join(BASE_DIR, 'scrapers', 'legends')

LEGENDS_JSON = os.path.join(LEGENDS_DIR, 'legends.json')
LEGEND_IMAGES_DIR = os.path.join(LEGENDS_DIR, 'legend_images')
LEGEND_ABILITY_IMAGES_DIR = os.path.join(LEGENDS_DIR, 'legend_ability_images')
LEGEND_TYPE_IMAGES_DIR = os.path.join(LEGENDS_DIR, 'legend_type_images')


# Weapons
WEAPONS_DIR = os.path.join(BASE_DIR, 'scrapers', 'weapons')

WEAPONS_JSON = os.path.join(WEAPONS_DIR, 'weapons.json')
AMMO_JSON = os.path.join(WEAPONS_DIR, 'weapon_ammo.json')
ATTACHMENTS_JSON = os.path.join(WEAPONS_DIR, 'weapon_attachments.json')
FIRE_MODES_JSON = os.path.join(WEAPONS_DIR, 'weapon_fire_modes.json')

WEAPON_IMAGES_DIR = os.path.join(WEAPONS_DIR, 'weapon_images')
WEAPON_AMMO_IMAGES_DIR = os.path.join(WEAPONS_DIR, 'weapon_ammo_images')
WEAPON_FIREMODE_IMAGES_DIR = os.path.join(WEAPONS_DIR, 'weapon_firemode_images')
WEAPON_ATTACHMENT_IMAGES_DIR = os.path.join(WEAPONS_DIR, 'weapon_attachment_images')
WEAPON_MODIFICATOR_IMAGES_DIR = os.path.join(WEAPONS_DIR, 'weapon_modificator_images')


# Creds (later move to .env)
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin'
ADMIN_CREDS = (ADMIN_USERNAME, ADMIN_PASSWORD)
