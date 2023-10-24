from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from music.youtube_music.music import TYMScraper
from music.deezer.scrapper import DeezerScrapper
from selenium.webdriver.common.proxy import Proxy, ProxyType
from proxy.proxy_extension.proxy_driver import get_chromedriver
from proxy.proxy_list.free_proxies import proxy_request
from music.soundcloud.scrapper import SoundCloudScrapper
from music.melon.scrapper import MelonScrapper
from music.spotify.scrapper import SpotifyScrapper
import time
import pandas as pd


def youtube_music():
    url = 'https://music.youtube.com/playlist?list=PL4fGSI1pDJn6OYkZx1Yd3kzV7eQzYXk7w'
    driver = get_chromedriver()
    tym = TYMScraper(url, driver)

    # save the songs to a csv file
    songs = tym.songs
    df = pd.DataFrame(songs)
    df.to_csv('songs.csv', index=False)
    

def deezer():
    url = 'https://www.deezer.com/en/channels/charts'

    driver = proxy_request()
    driver.maximize_window()

    dz = DeezerScrapper(url, driver)
    page_source = dz.get_songs()

    # save the songs to a csv file
    df = pd.DataFrame(page_source, columns=['Song', 'Artist', 'Album', 'Duration'])
    df.to_csv('deezer_songs.csv', index=False)

def sound_cloud():
    url = 'https://soundcloud.com/charts/top?genre=all-music&country=US'
    driver = proxy_request()
    driver.maximize_window()

    time.sleep(5)
    sc = SoundCloudScrapper(url, driver)
    page_source = sc.get_songs()

    # save the songs to a csv file
    df = pd.DataFrame(page_source)
    df.to_csv('soundcloud_songs.csv', index=False)

def melon():
    url = 'https://www.melon.com/chart/week/index.htm'
    driver = proxy_request()
    driver.maximize_window()

    time.sleep(5)
    ml = MelonScrapper(url, driver)
    page_source = ml.get_songs()

    # save the songs to a csv file
    df = pd.DataFrame(page_source)
    df.to_csv('melon_songs.csv', index=False)

def spotify():
    url = 'https://charts.spotify.com/home'
    driver = proxy_request()
    driver.maximize_window()

    time.sleep(5)
    sp = SpotifyScrapper(url, driver)
    page_source = sp.get_songs()

    # save the songs to a csv file
    df = pd.DataFrame(page_source)
    df.to_csv('spotify_songs.csv', index=False)

def main():
    # youtube_music()
    # deezer()
    # sound_cloud()
    # melon()
    spotify()

if __name__ == '__main__':
    main()