import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

LEGENDS_JSON = os.path.join(BASE_DIR, 'scrapers', 'legends', 'legends.json')
LEGEND_IMAGES_DIR = os.path.join(BASE_DIR, 'scrapers', 'legends', 'legend_images')
LEGEND_ABILITY_IMAGES_DIR = os.path.join(BASE_DIR, 'scrapers', 'legends', 'legend_ability_images')

WEAPONS_JSON = os.path.join(BASE_DIR, 'scrapers', 'weapons', 'weapons.json')

LOCAL_BASE_API_URL = 'http://localhost:8000/api/v1'
HEROKU_DEV_BASE_API_URL = 'https://apex-buff-development.herokuapp.com/api/v1'

ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin'

MAX_WAIT = 10
PAUSE = 0.3
