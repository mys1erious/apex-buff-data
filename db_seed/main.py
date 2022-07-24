import re

from legends import seed as legends_seed
from weapon_deps import seed as weapon_deps_seed
from weapons import seed as weapons_seed


if __name__ == '__main__':
    legends_seed()
    weapon_deps_seed()
    weapons_seed()
