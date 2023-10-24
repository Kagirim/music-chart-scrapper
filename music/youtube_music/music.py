from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
import time
from selenium.webdriver.common.proxy import Proxy, ProxyType

class TYMScraper():
    def __init__(self, url, driver):
        self.driver = driver
        self.base_url = url
        self.driver.implicitly_wait(10)

        self.driver.get(self.base_url)
        time.sleep(2)

    def get_songs(self):
        # get the div with class="chart-table style-scope ytmc-chart-table"
        songs_div = self.driver.find_element(By.XPATH, "//div[@class='chart-table style-scope ytmc-chart-table']")

        # get the div inside the div with class current-rank style-scope ytmc-chart-table
        song_rank = songs_div.find_elements(By.XPATH, "//div[@class='current-rank style-scope ytmc-chart-table']//div[@class='rank style-scope ytmc-chart-table']")
        song_rank = [rank.text for rank in song_rank]

        # get song title from the text of the div with class="ytmc-ellipsis-text style-scope"
        song_titles = songs_div.find_elements(By.XPATH, "//div[@class='ytmc-ellipsis-text-container style-scope ytmc-ellipsis-text']/span")
        song_titles = [song.text if song.text is not None and song.text != '' else ' ' for song in song_titles]
        song_titles = list(set(song_titles))
        
        # get song artist from span within div with class="ytmc-artist-name clickable style-scope ytmc-artists-list"
        song_artists = []
        song_artists_div = songs_div.find_elements(By.XPATH, "//div[@class='ytmc-artists-list-container style-scope ytmc-artists-list']")
        for artist in song_artists_div:
            artist_name = artist.find_element(By.TAG_NAME, 'span')
            song_artists.append(artist_name.text)

        # get song views text from span inside div with class views style-scope ytmc-chart-table
        song_views = songs_div.find_elements(By.XPATH, "//div[@class='views style-scope ytmc-chart-table']/span")
        song_views = [view.text if view.text is not None and view.text != '' else ' ' for view in song_views]

        # store song title, artist, and views in a dictionary
        song_dict = {'rank': song_rank, 'title': song_titles[:-1], 'artist': song_artists, 'views': song_views}

        return song_dict

