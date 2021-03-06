import re
import json

from dataclasses import dataclass, fields
from selenium.webdriver.common.by import By

from constants import *
from utils.utils import (
    BaseDataclass,
    BaseScraper,
    cut_to_end_pattern,
    get_attrs_from_json,
    save_to_json
)


@dataclass
class Ability(BaseDataclass):
    name: str
    icon_url: str
    type: str
    description: str
    cooldown: str
    info: str

    def __init__(self):
        super().__init__()


@dataclass
class Legend(BaseDataclass):
    name: str
    icon_url: str
    role: str
    real_name: str
    gender: str
    age: int
    homeworld: str
    legend_type: str
    abilities: list[Ability]
    lore: str

    def __init__(self):
        super().__init__()

    def to_dict(self):
        data = {}
        abilities = []

        for ability in self.abilities:
            abilities.append(ability.to_dict())

        for field in fields(self):
            if field.name == 'abilities':
                data[field.name] = abilities
            else:
                data[field.name] = getattr(self, field.name)

        return data


class LegendsScraper(BaseScraper):

    def __init__(self):
        super().__init__()

        self.legends_base_url = 'https://apexlegends.fandom.com/wiki/Apex_Legends_Wiki'
        self.legends = []

    def scrape(self):
        self.browser = self.browser()
        self.browser.get(self.legends_base_url)
        self.accept_cookies()

        names, hrefs, icon_srcs = self.scrape_legends_base_page()

        for i in range(len(hrefs)):
            legend_obj = Legend()

            legend_obj.icon_url = icon_srcs[i]
            self.scrape_legend_detail_page(legend_obj, hrefs[i])

            self.legends.append(legend_obj)

        self.browser.quit()
        return self.legends

    def scrape_legend_detail_page(self, legend_obj, href):
        self.browser.get(href)
        self.wait_for_redirect(href)

        self.set_legend_info_from_infobox_table(legend_obj)
        self.set_legend_abilities(legend_obj)
        self.set_legend_lore(legend_obj)

    def set_legend_lore(self, legend_obj):
        legend_obj.lore = self.browser.find_element(
            by=By.XPATH,
            value='//*[@id="mw-content-text"]/div/table[3]/tbody/tr[1]'
        ).text

    def set_legend_abilities(self, legend_obj):
        abilities = []
        ability_container = self.browser.find_elements(by=By.CLASS_NAME, value='ability-container')

        for ability in ability_container:
            table = ability.find_element(by=By.CSS_SELECTOR, value='table[class="wikitable ability"]')

            ability_obj = Ability()

            ability_obj.type = table.find_element(by=By.XPATH, value='./tbody/tr[1]/th[1]').text.lower()
            ability_obj.name = table.find_element(by=By.XPATH, value='./tbody/tr[2]/th').text.title()
            ability_obj.description = table.find_element(by=By.XPATH, value='./tbody/tr[3]/td').text
            ability_obj.cooldown = table.find_element(by=By.XPATH, value='./tbody/tr[4]/td').text

            full_icon_url = table.find_element(by=By.XPATH, value='./tbody/tr[1]/td/a').get_attribute('href')
            icon_url = cut_to_end_pattern(full_icon_url, '.svg')
            ability_obj.icon_url = icon_url

            tabber = ability.find_element(
                by=By.CLASS_NAME,
                value='tabber-ability'
            )

            # For now only if Info tab is selected by default
            selected_tab = tabber.find_element(by=By.CLASS_NAME, value='wds-is-current').text.lower()
            if selected_tab == 'info':
                info_content = tabber.find_element(
                    by=By.CSS_SELECTOR,
                    value='div[class="wds-tab__content wds-is-current"]'
                ).text
                ability_obj.info = info_content
            else:
                ability_obj.info = None

            abilities.append(ability_obj)

        legend_obj.abilities = abilities

    def set_legend_info_from_infobox_table(self, legend_obj):
        infobox_table = self.browser.find_element(by=By.XPATH, value='//table[@class="infobox-table"]')

        legend_obj.name = infobox_table.find_element(
            by=By.XPATH, value='.//th[@class="infobox-header"]'
        ).text
        legend_obj.role = infobox_table.find_elements(
            by=By.XPATH, value='.//td[@class="infobox-centered"]'
        )[1].text

        infobox_rows = infobox_table.find_elements(
            by=By.XPATH, value='.//tr[@class="infobox-row"]'
        )

        for row in infobox_rows:
            attr_name = row.find_element(by=By.XPATH, value='.//th[@class="infobox-row-name"]').text
            attr_name = attr_name.lower().replace(' ', '_')

            if attr_name in legend_obj.field_names:
                attr_value = row.find_element(by=By.XPATH, value='.//td[@class="infobox-row-value"]').text

                # Getting max integer from age row
                if attr_name == 'age':
                    attr_value = max(map(int, re.findall(r'\d+', attr_value)))

                # Changing gender to its abbreviation
                if attr_name == 'gender':
                    attr_value = self.gender_processing(attr_value)

                if attr_name == 'legend_type':
                    attr_value = attr_value.lower()

                legend_obj.__setattr__(attr_name, attr_value)

    def gender_processing(self, attr_value):
        gender_abbreviations = {
            'Male': 'm',
            'Female': 'f',
            'Non-binary': 'nb'
        }

        return gender_abbreviations[attr_value]

    def scrape_legends_base_page(self):
        legend_elements = self.get_legend_elements()
        num_of_legend_elements = len(legend_elements)

        names = self.get_legend_names(legend_elements)
        hrefs = self.get_legend_hrefs(legend_elements)
        icon_srcs = self.get_legend_icon_srcs(legend_elements)

        if all(len(lst) == num_of_legend_elements for lst in [names, hrefs, icon_srcs]):
            pass
        else:
            raise ValueError(
                f'len(names): {len(names)}, '
                f'len(hrefs): {len(hrefs)}, '
                f'len(icon_srcs): {len(icon_srcs)} '
                f'are not equal'
            )

        return names, hrefs, icon_srcs

    def get_legend_icon_srcs(self, legend_elements):
        icon_srcs = []
        for le in legend_elements:
            icon_srcs.append(self.get_legend_icon_src(le))
        return icon_srcs

    def get_legend_icon_src(self, legend_element):
        full_src = legend_element.find_element(by=By.TAG_NAME, value='img').get_attribute('src')
        src = cut_to_end_pattern(full_src, '.png')
        return src

    def get_legend_hrefs(self, legend_elements):
        hrefs = []
        for le in legend_elements:
            hrefs.append(le.find_element(by=By.TAG_NAME, value='a').get_attribute('href'))
        return hrefs

    def get_legend_names(self, legend_elements):
        names = []
        for le in legend_elements:
            names.append(le.find_element(by=By.TAG_NAME, value='a').get_attribute('title'))
        return names

    def get_legend_elements(self):
        legends_section = self.browser.find_element(by=By.ID, value='fp-1')
        legend_links_container = legends_section.find_element(by=By.CLASS_NAME, value='fplinks')
        legends = legend_links_container.find_elements(
            by=By.XPATH,
            value='.//div[@class="fplink-outer plainlinks"]'
        )

        scroll_step_y = 100
        scroll_to_y = scroll_step_y
        for legend in legends:
            # Waiting for image url to load to not get output like:
            #     data:image/gif;base64...
            self.wait_for(
                lambda: self.assert_func(
                    item1=legend.find_element(
                        by=By.TAG_NAME, value='img'
                    ).get_attribute('src').startswith('https://'),
                    item2=True
                )
            )

            # Scrolling for images to load
            self.browser.execute_script(f'window.scrollTo(0, {scroll_to_y})')
            scroll_to_y += scroll_step_y

        return legends

    def accept_cookies(self):
        accept_btn = self.wait_for(
            lambda: self.browser.find_element(
                by=By.CSS_SELECTOR,
                value='.NN0_TB_DIsNmMHgJWgT7U'
            )
        )
        accept_btn.click()

    def save_to_json(self, path):
        data = {'legends': [legend.to_dict() for legend in self.legends]}
        save_to_json(path, data)

    def download_images(self, path, names, links, prefix=''):
        self.browser = self.browser()

        for i in range(len(names)):
            full_name = names[i]

            if isinstance(prefix, list) and len(prefix) == len(names):
                full_name = f'{prefix[i]}_{names[i]}'
                full_name = full_name.replace(' ', '_').lower()

            self.browser.get(links[i])
            self.browser.save_screenshot(f'{path}/{full_name}.png')

        self.browser.quit()


def scrape_legends_to_json(scraper):
    legends = scraper.scrape()
    scraper.save_to_json(LEGENDS_JSON)


def download_legend_icons(scraper):
    with open(LEGENDS_JSON, 'r') as f:
        legends_json = json.load(f)['legends']
        legend_attrs = ['name', 'icon_url']
        legends_data = get_attrs_from_json(legends_json, legend_attrs)

        scraper.download_images(
            LEGEND_IMAGES_DIR,
            legends_data['names'],
            legends_data['icon_urls']
        )


def download_legend_ability_icons(scraper):
    with open(LEGENDS_JSON, 'r') as f:
        legends_json = json.load(f)['legends']
        ability_attrs = ['name', 'icon_url']
        abilities_data = {
            'legends': [],
            'names': [],
            'icon_urls': []
        }

        for legend in legends_json:
            for ability in legend['abilities']:
                abilities_data['legends'].append(legend['name'])
                abilities_data['names'].append(ability['name'])
                abilities_data['icon_urls'].append(ability['icon_url'])

        scraper.download_images(
            LEGEND_ABILITY_IMAGES_DIR,
            abilities_data['names'],
            abilities_data['icon_urls'],
            prefix=abilities_data['legends']
        )


if __name__ == '__main__':
    # legends_scraper = LegendsScraper()
    # scrape_legends_to_json(legends_scraper)
    #
    # download_legend_icons(legends_scraper)
    # download_legend_ability_icons(legends_scraper)

    ...
