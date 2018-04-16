import sys, re
import urllib.request,  urllib.error
from bs4 import BeautifulSoup
from requests import get
from time import sleep
from random import randint


class Azlyrics(object):

    def __init__(self, artist, music):
        self.artist = artist
        self.music = music
        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; LCJB; rv:11.0) like Gecko",
                        "Connection": "Keep-Alive",
                        "Content-Type": "application/x-www-form-urlencoded"}

    def normalize_str(self, str):
        return re.sub(r'\W+', '', str.lower())

    def normalize_artist_music(self):
        return self.normalize_str(self.artist), self.normalize_str(self.music)

    def url(self):
        if not self.artist and not self.music:
            self.artist = "rickastley"
            self.music = "nevergonnagiveyouup"
        return "http://azlyrics.com/lyrics/{}/{}.html".format(*self.normalize_artist_music())

    def get_page(self):
        try:
            sleep(randint(2, 4))
            url = get(self.url(), headers=self.headers)
            return url.text
        except urllib.error.HTTPError as e:
            if e.code == 404:
                print("Music not found")
                sys.exit(1)

    def extract_lyrics(self, page):
        soup = BeautifulSoup(page, "html.parser")
        try:
            section_container = soup.find('div', {'class': 'col-xs-12 col-lg-8 text-center'})
            lyrics = list(section_container.find_all('div'))[6].text
            print(self.format_title())
        except AttributeError:
            print("Lyrics nor found!!")
            return ''
        return lyrics

    def format_lyrics(self, lyrics):
        formated_lyrics = "\n".join(lyrics)
        return formated_lyrics

    def format_title(self):
        return "{} by {}".format(self.music.title(), self.artist.title())

    def get_lyrics(self):
        page = self.get_page()
        lyrics = self.extract_lyrics(page)
        return lyrics
