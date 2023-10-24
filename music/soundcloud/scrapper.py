from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver import ActionChains
import time

class SoundCloudScrapper():
    def __init__(self, url, driver):
        self.url = url
        self.driver = driver
        self.driver.implicitly_wait(10)
        self.driver.get(self.url)

    def accept_cookies(self):
        get_btn = self.driver.find_element(By.XPATH, "//button[@id='onetrust-accept-btn-handler']")
        return get_btn

    def get_songs(self):
        WebDriverWait(self.driver, 10).until(expected_conditions.presence_of_element_located((By.XPATH, "//button[@id='onetrust-accept-btn-handler']")))
        self.accept_cookies().click()
        time.sleep(1)

        # get the songs
        song_div = self.driver.find_element(By.XPATH, "//ul[@class='lazyLoadingList__list sc-list-nostyle sc-clearfix']")

        song_list = []
        while True:
            songs = song_div.find_elements(By.XPATH, "//li[@class='chartTracks__item']")

            for song in songs:
                song_details = song.text.split('\n')
                try:
                    song_details.remove("Not available in Kenya")
                except:
                    pass
                    
                if song_details not in song_list:
                    song_list.append(song_details[:4])

            # scroll down
            current_pos = self.driver.execute_script("return window.pageYOffset;")

            ActionChains(self.driver).send_keys(Keys.PAGE_DOWN).perform()
            time.sleep(1)

            if current_pos == self.driver.execute_script("return window.pageYOffset;"):
                break

        return list(set(song_list))
        