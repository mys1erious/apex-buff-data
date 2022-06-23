import time
from dataclasses import (
    dataclass,
    fields,
    is_dataclass,
    asdict
)
import json

from selenium import webdriver
from selenium.common import WebDriverException

from .constants import *


def wait(fn):
    def modified_fn(*args, **kwargs):
        start_time = time.time()
        while True:
            try:
                return fn(*args, **kwargs)
            except (AssertionError, WebDriverException) as e:
                if time.time() - start_time > MAX_WAIT:
                    raise e
                time.sleep(PAUSE)

    return modified_fn


@wait
def wait_for(fn):
    return fn()


class BaseScraper:
    def __init__(self):
        self.browser = webdriver.Firefox()

    @wait
    def wait_for_redirect(self, new_url):
        assert self.browser.current_url, new_url

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.browser.quit()


@dataclass
class BaseDataclass:
    def __init__(self, *args, **kwargs):
        for field in fields(self):
            if field.name not in kwargs:
                setattr(self, field.name, None)

    @property
    def field_names(self):
        lst = []
        for field in fields(self):
            lst.append(field.name)
        return lst

    def to_dict(self):
        data = {}

        for field in fields(self):
            data[field.name] = getattr(self, field.name)

        return data
