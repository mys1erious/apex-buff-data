import dataclasses
import re
from dataclasses import dataclass, fields
import time
import json

from selenium.webdriver import Keys
from selenium.webdriver.common.by import By

from data.scrapers.utils.constants import *
from data.scrapers.utils.utils import (
    BaseDataclass,
    BaseScraper,
    wait_for
)


@dataclass
class Legend(BaseDataclass):
    name: str
    icon: str
    role: str
    real_name: str
    gender: str
    age: int
    homeworld: str
    legend_type: str
    lore: str

    def __init__(self):
        super().__init__()


@dataclass
class Ability(BaseDataclass):
    character_name: str
    name: str
    icon: str
    ability_type: str
    description: str
    cooldown: float
    info: str
    interactions: str
    tips: str
    arenas: str

    def __init__(self):
        super().__init__()


class LegendsScraper(BaseScraper):
    """
    For now scrapes:
    name
    role
    real_name
    gender
    age(last int value, rework later)
    homeworld
    legend_type(rework to get image image)
    """

    def __init__(self):
        super().__init__()
        self.apex_wiki_base_url = 'https://apexlegends.fandom.com/wiki/Apex_Legends_Wiki'

        self.legends_list = []

        self.scrape()
        self.export_legends_to_json()

    def __exit__(self, exc_type, exc_val, exc_tb):
        super().__exit__(exc_type, exc_val, exc_tb)

    def scrape(self):
        self.browser.get(self.apex_wiki_base_url)
        self.accept_cookies()

        legends_hrefs = self.get_legends_hrefs()

        for legend_href in legends_hrefs:
            self.browser.get(legend_href)
            self.wait_for_redirect(legend_href)
            legend_obj = Legend()

            self.infobox_table = wait_for(
                lambda: self.browser.find_element(by=By.XPATH, value='//table[@class="infobox-table"]')
            )
            self.set_legend_info_from_infobox_table(legend_obj)

            self.legends_list.append(legend_obj)
            print(legend_obj)

    def set_legend_info_from_infobox_table(self, legend_obj):
        legend_obj.name = self.infobox_table.find_element(
            by=By.XPATH, value='.//th[@class="infobox-header"]'
        ).text

        legend_obj.role = self.infobox_table.find_elements(
            by=By.XPATH, value='.//td[@class="infobox-centered"]'
        )[1].text

        infobox_rows = self.infobox_table.find_elements(
            by=By.XPATH, value='.//tr[@class="infobox-row"]'
        )
        for row in infobox_rows:
            attr_name = row.find_element(by=By.XPATH, value='.//th[@class="infobox-row-name"]').text
            attr_name = attr_name.lower().replace(' ', '_')

            if attr_name in legend_obj.field_names:
                attr_value = row.find_element(by=By.XPATH, value='.//td[@class="infobox-row-value"]').text

                # Getting last integer from age row
                if attr_name == 'age':
                    attr_value = re.findall(r'\d+', attr_value)[-1]
                    attr_value = int(attr_value)

                # For now changing legend_type to None due to not having LegendType Model objects
                if attr_name == 'legend_type':
                    attr_value = None

                # Changing gender to its abbreviation
                if attr_name == 'gender':
                    if attr_value == 'Male':
                        attr_value = 'm'
                    if attr_value == 'Female':
                        attr_value = 'f'
                    if attr_value == 'Non-binary':
                        attr_value = 'nb'

                legend_obj.__setattr__(attr_name, attr_value)

    def get_legends_hrefs(self):
        hrefs = []
        legends = self.get_legends_list()

        for legend in legends:
            href = legend.find_element(by=By.TAG_NAME, value='a').get_attribute('href')
            hrefs.append(href)

        return hrefs

    def get_legends_list(self):
        container = self.browser \
            .find_element(by=By.ID, value='fp-1') \
            .find_element(by=By.CLASS_NAME, value='fplinks')
        legends = container.find_elements(by=By.XPATH, value='.//div[@class="fplink-outer plainlinks"]')

        return legends

    def accept_cookies(self):
        accept_btn = wait_for(lambda: self.browser.find_element(by=By.CSS_SELECTOR, value='.NN0_TB_DIsNmMHgJWgT7U'))
        accept_btn.click()

    def export_legends_to_json(self):
        data = {'legends': [legend.to_dict() for legend in self.legends_list]}

        with open(LEGENDS_JSON, 'w') as f:
            json.dump(data, f, indent=4)


if __name__ == '__main__':
    LegendsScraper()

