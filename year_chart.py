from bs4 import BeautifulSoup
from requests import get
from collections import defaultdict
from lyrics import Azlyrics
import re
import json
from time import sleep
from random import randint


class YearChartCrawl(object):
    def __init__(self, year):
        self.year = year
        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; LCJB; rv:11.0) like Gecko",
                        "Connection": "Keep-Alive",
                        "Content-Type": "application/x-www-form-urlencoded"}
        self.orig_url = "https://www.billboard.com"
        self.orig_entry = "/charts/{}/year-end".format(year)

    def review_extraction(self, items_container):
        """get a set of data from a block"""
        rank = items_container['data-item-rank']
        title = items_container.find('div', {'class': 'ye-chart-item__title'}).text.strip()  # could be song name, artist name, album name...
        artist_name = items_container.find('div', {'class': 'ye-chart-item__artist'}).text.strip()
        artist_link = items_container.find('div', {'class': 'ye-chart-item-expanded__artist'})
        artist_link = artist_link.a['href'] if artist_link else ''
        image = items_container.find('div', {'class': 'ye-chart-item__image'}).img['src']
        image = image.split('/', 4)[-1]  # no need to store the same prefix: 'https://charts-static.billboard.com/img'

        return rank, title, artist_name, artist_link, image

    def chart_links(self, orig_url, orig_entry):
        """get links to different charts for a specific year"""
        url = get(orig_url + orig_entry)
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

    def data_scraping(self):
        """scrape data from charts for a specific year, and store it as a json file"""
        # TODO: maybe store them in a database
        chart_entries = self.chart_links(self.orig_url, self.orig_entry)
        data_dict = defaultdict(dict)
        for entry in chart_entries:
            chart_title = entry.split('/')[-1]
            print("{} ----> done!".format(chart_title))
            url = get(self.orig_url + entry)
            # sleep(randint(1, 3))
            page_html = BeautifulSoup(url.text, 'html.parser')
            section_container = page_html.find_all('div', {'class': 'chart-details__item-list'})  # 20 items per group
            items_container = []
            for i in range(len(section_container)):
                items_container.extend(list(section_container[i].find_all('article', {'class': 'ye-chart-item'})))
            for item in items_container:
                rank, title, artist_name, artist_link, image = self.review_extraction(item)
                temp_dict = {'rank': rank, 'title': title, 'artist_name': artist_name,
                             'artist_link': artist_link, 'image_link': image}
                if 'song' in chart_title:
                    az = Azlyrics(artist_name, title)
                    lyrics = az.get_lyrics()
                    temp_dict['lyrics'] = lyrics
                data_dict[chart_title][rank] = temp_dict
        json_data = json.dumps(data_dict)
        with open('data.json', 'w') as f:
            f.write(json_data)
        print("finished!")


if __name__ == "__main__":
    yc = YearChartCrawl('2017')
    yc.data_scraping()
    # yc.lyric_scraping()
    # with open('data.json', 'r') as f:
    #     data = json.load(f)
    #     for _ in data:
    #         print(_)
    # for cha in data['hot-100-songs'].items():
    #     title = cha[1]['title']
    #     name = cha[1]['artist_name']
    #     az = Azlyrics(name, title)
    #     print(az.format_title())
    #     print(az.get_lyrics())



