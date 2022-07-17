import re
import time
from dataclasses import (
    dataclass,
    fields
)
import json
import cv2

from selenium import webdriver
from selenium.common import WebDriverException

from constants import *


def cut_to_end_pattern(text, patterns, include_pattern=True):
    for pattern in patterns:
        n = len(pattern)
        ind = text.find(pattern)

        if include_pattern:
            ind += n

        if ind > n:
            return text[:ind]

    return ''


def slugify(s):
    s = s.lower().strip()
    s = re.sub(r'[^\w\s-]', '', s)
    s = re.sub(r'[\s_-]+', '-', s)
    s = re.sub(r'^-+|-+$', '', s)
    return s


def save_to_json(path, data):
    with open(path, 'w') as outfile:
        json.dump(data, outfile, indent=2)


def load_json_data(file):
    with open(file, 'r') as f:
        data = json.load(f)

        return data


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


class BaseScraper:
    def __init__(self):
        self.browser = lambda: webdriver.Firefox()

    def assert_func(self, item1, item2):
        assert item1, item2

    @wait
    def wait_for(self, fn):
        return fn()

    @wait
    def wait_for_redirect(self, new_url):
        assert self.browser.current_url, new_url


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
