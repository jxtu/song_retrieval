from bs4 import BeautifulSoup
from requests import get
from time import sleep
from random import randint
import re


class Biography(object):

    def __init__(self, name):
        self.name = name
        self.main_link = 'https://www.biography.com'

    def poeple_links(self):
        normalized_name = '%20'.join(self.name.split()).lower()
        url = get('https://www.biography.com/search?query={}'.format(normalized_name))
        page_html = BeautifulSoup(url.text, 'html.parser')
        related_links = page_html.find_all('phoenix-super-link', {'href': re.compile(r'/people/.*')})
        links_list = [link['href'] for link in related_links] if related_links else []
        self.main_link = self.main_link + links_list[0] if len(links_list) > 0 else None
        return links_list

    def abstract(self):
        if self.main_link:
            print(self.main_link)
            sleep(randint(0, 2))
            url = get(self.main_link)
            page_html = BeautifulSoup(url.text, 'html.parser')
            abstract = page_html.find('div', {'class': 'm-person--abstract l-person--abstract'})
            return abstract.text if abstract else None
        else:
            return None

    def people_abstract(self, link=None):
        if link:
            print(link)
            url = get(link)
            page_html = BeautifulSoup(url.text, 'html.parser')
            abstract = page_html.find('div', {'class': 'm-person--abstract l-person--abstract'}).text
            return abstract
        else:
            return None


