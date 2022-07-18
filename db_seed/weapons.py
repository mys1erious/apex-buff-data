# def post_ammo_type(url, data):
#     data.pop('img')
#     data['name'] = data['name'].title()
#     img_path = f'{WEAPON_AMMO_IMAGES_DIR}/{data["name"].title()}.png'
#
#     with open(img_path, 'rb') as img:
#         response = requests.post(
#             url=url,
#             data=data,
#             files={'icon': img},
#             auth=(ADMIN_USERNAME, ADMIN_PASSWORD)
#         )
#         if not response.ok:
#             print(data['name'], response)
#
#
# def post_ammo_types(url):
#     data = load_json_data(WEAPONS_DIR+'/weapon_ammo.json')
#     for item in data['ammo']:
#         item['name'] = item['name'].lower()
#         post_ammo_type(url, data=item)
#
#
# def post_firemode(url, data):
#     data.pop('img')
#     img_path = f'{WEAPON_FIREMODE_IMAGES_DIR}/{data["name"]}.png'
#
#     with open(img_path, 'rb') as img:
#         response = requests.post(
#             url=url,
#             data=data,
#             files={'icon': img},
#             auth=(ADMIN_USERNAME, ADMIN_PASSWORD)
#         )
#         if not response.ok:
#             print(data['name'], response)
#
#
# def post_firemods(url):
#     data = load_json_data(WEAPONS_DIR+'/weapon_firemods.json')
#     for item in data['firemods']:
#         post_firemode(url, data=item)
#


# def get_damage_data_from_weapon(weapon):
#     suffix = '_damage'
#     str_fields = ['body_damage', 'head_damage', 'legs_damage']
#     data = {}
#
#     for field in str_fields:
#         suffix_ind = field.find(suffix)
#         data[field[:suffix_ind]] = weapon[field]
#
#     return data


# def get_ammo_data_from_weapon(weapon):
#     return {'ammo': weapon['weapon_ammo']}


# def get_firemods_data_from_weapon(weapon):
#     # Check for len of firemods to be = to dps and ttk and rpm
#     # otherwise get values from previous index in list to be the next
#     data = {'firemods': []}
#     fields = ['dps', 'ttk', 'rpm']
#
#     firemode_slugs = [slugify(s) for s in weapon['fire_modes']]
#     for i, firemode_slug in enumerate(firemode_slugs):
#         firemode = {'firemode_slug': firemode_slug, 'dps': None, 'ttk': None, 'rpm': None}
#         for field in fields:
#             try:
#                 firemode[field] = weapon[field][i]
#             except IndexError:
#                 firemode[field] = weapon[field][0]
#
#         data['firemods'].append(firemode)
#
#     return data


def post_attachment(url, data):
    data.pop('img')
    img_path = f'{WEAPON_ATTACHMENT_IMAGES_DIR}/{data["name"]}.png'

    with open(img_path, 'rb') as img:
        response = requests.post(
            url=url,
            data=data,
            files={'icon': img},
            auth=(ADMIN_USERNAME, ADMIN_PASSWORD)
        )
        if not response.ok:
            print(data['name'], response.json)


def post_attachments(url):
    data = load_json_data(WEAPONS_DIR+'/weapon_attachments.json')
    for item in data['attachments']:
        post_attachment(url, data=item)


def post_weapon(weapon, url):
    weapon_data = get_weapon_data_from_weapon(weapon)
    attachments_data = get_attachments_data_from_weapon(weapon)

    # damage_data = get_damage_data_from_weapon(weapon)
    # ammo_data = get_ammo_data_from_weapon(weapon)
    # firemods_data = get_firemods_data_from_weapon(weapon)

    weapon_name = weapon_data.get('name')
    weapon_img_path = weapon_data.pop('weapon_img_path')

    with open(weapon_img_path, 'rb') as img:
        post_weapon_response = requests.post(
            url=url,
            data=weapon_data,
            files={'icon': img},
            auth=ADMIN_CREDS
        )

    # if post_weapon_response.ok:
    #
    #     post_damage_response = requests.post(
    #         url=weapon_url+'/damage/',
    #         data=damage_data,
    #         auth=ADMIN_CREDS
    #     )
    #     put_ammo_response = requests.put(
    #         url=weapon_url+'/ammo/',
    #         data=ammo_data,
    #         auth=ADMIN_CREDS
    #     )
    #
    #     for firemode in firemods_data['firemods']:
    #         post_weapon_firemode_response = requests.post(
    #             url=weapon_url+'/firemods/',
    #             data=firemode,
    #             auth=ADMIN_CREDS
    #         )
    #
    #     print(f'{weapon_name} post_damage: {post_damage_response.ok}')
    #     print(f'{weapon_name} put_ammo: {put_ammo_response.ok}')
    #
    #     try: print(f'{weapon_name} post_weapon_attachment: {post_weapon_attachment_response.ok}')
    #     except UnboundLocalError: pass
    #     try: print(f'{weapon_name} post_weapon_firemode: {post_weapon_firemode_response.ok}')
    #     except UnboundLocalError: pass
    #
    #     print(f'{weapon_name}: DONE\n')
    # else:
    #     print(f'{weapon_name}: {post_weapon_response}')
    #     try:
    #         print(post_weapon_response.json())
    #     except Exception:
    #         pass
