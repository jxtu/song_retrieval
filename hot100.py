"""
uber reviews from https://www.consumeraffairs.com/travel/uber.html
"""

from bs4 import BeautifulSoup
from requests import get
import re
from time import sleep
from random import randint

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; LCJB; rv:11.0) like Gecko",
           "Connection": "Keep-Alive",
           "Content-Type": "application/x-www-form-urlencoded"
           }
orig_url = "https://www.billboard.com"
orig_entry = "/charts/2017/year-end"


def review_extraction(items_container):
    rank = items_container['data-item-rank']
    song_name = items_container.find('div', {'class': 'ye-chart-item__title'}).text.strip()
    artist_name = items_container.find('div', {'class': 'ye-chart-item__artist'}).text.strip()
    artist_link = items_container.find('div', {'class': 'ye-chart-item-expanded__artist'})
    artist_link = artist_link.a['href'] if artist_link else ''
    return rank, song_name, artist_name, artist_link


def next_page(url):
    page_html = BeautifulSoup(url.text, 'html.parser')
    navigation_html = page_html.find('nav', {'class': 'prf-pgr js-profile-pager'})
    next_page_html = navigation_html.find('a', {'rel': 'next'})
    return next_page_html['href'] if next_page_html else next_page_html


def chart_links(orig_url, entry):
    url = get(orig_url + entry)
    # sleep(randint(1, 3))
    page_html = BeautifulSoup(url.text, 'html.parser')
    panel = page_html.find('div', {'class': 'chart-panel', 'id': 'overallChartPanel'}).children
    links_list = []
    for col in panel:
        try:
            links = col.find_all('div', {'class': re.compile('chart-panel__item.*')})
        except AttributeError:
            continue
        for link in links:
            try:
                links_list.append(link.a['href'])
            except TypeError:
                continue
    return links_list


def data_scraping(entry):
    url = get(orig_url + entry)
    data = []
    # sleep(randint(1, 3))
    page_html = BeautifulSoup(url.text, 'html.parser')
    section_container = page_html.find_all('div', {'class': 'chart-details__item-list'})  # 20 items per group
    items_container = []
    for i in range(len(section_container)):
        items_container.extend(list(section_container[i].find_all('article', {'class': 'ye-chart-item'})))
    for item in items_container:
        data.append(review_extraction(item))
    return data


if __name__ == '__main__':
    ll = chart_links(orig_url, orig_entry)
    print(ll)
    # a = data_scraping(ll[0])
    # print(a)

