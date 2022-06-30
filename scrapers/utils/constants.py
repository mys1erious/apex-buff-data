import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

LEGENDS_JSON = os.path.join(BASE_DIR, 'legends', 'legends.json')
LEGEND_IMAGES_DIR = os.path.join(BASE_DIR, 'legends', 'legend_images')
LEGEND_ABILITY_IMAGES_DIR = os.path.join(BASE_DIR, 'legends', 'legend_ability_images')

WEAPONS_JSON = os.path.join(BASE_DIR, 'weapons', 'weapons.json')

MAX_WAIT = 10
PAUSE = 0.3
