from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
import time


class MelonScrapper():
    def __init__(self, url, driver):
        self.url = url
        self.driver = driver
        self.driver.implicitly_wait(10)
        self.driver.get(self.url)

    def get_songs(self):
        # get the song table
        song_table = self.driver.find_element(By.TAG_NAME, "table")

        # get the song header
        song_header = song_table.find_element(By.TAG_NAME, "thead").text.split('\n')

        # get the song body
        song_body = song_table.find_element(By.TAG_NAME, "tbody")

        song_list = []

        while True:
            songs = song_body.find_elements(By.XPATH, "//tr[@class='lst50']")

            for song in songs:
                song_details = song.text.split('\n')
                if song_details not in song_list:
                    song_details = song_details[:4]
                    del song_details[1]

                    song_list.append(song_details[:4])

            # scroll down
            current_pos = self.driver.execute_script("return window.pageYOffset;")

            ActionChains(self.driver).send_keys(Keys.PAGE_DOWN).perform()
            time.sleep(1)

            if current_pos == self.driver.execute_script("return window.pageYOffset;"):
                break

        return song_list