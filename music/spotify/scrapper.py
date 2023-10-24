from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver import ActionChains
import time


class SpotifyScrapper():
    def __init__(self, url, driver):
        self.url = url
        self.driver = driver
        self.driver.implicitly_wait(10)
        self.driver.get(self.url)

    def get_songs(self):
        # WebDriverWait(self.driver, 10).until(expected_conditions.presence_of_element_located((By.XPATH, "//button[@id='onetrust-accept-btn-handler']")))
        # self.driver.find_element(By.XPATH, "//button[@id='onetrust-accept-btn-handler']").click()
        # time.sleep(1)

        # get the songs
        song_div = self.driver.find_element(By.XPATH, "//ol[@class='ChartsHomeEntries__ChartEntries-kmpj2i-0 gunxSo']")

        # move to the songs section
        self.driver.execute_script("arguments[0].scrollIntoView();", song_div)

        song_list = []
        while True:
            songs = song_div.find_elements(By.XPATH, "//li[@data-testid='charts-entry-item']")
            
            for song in songs:
                song_details = song.text.split('\n')
                                   
                if song_details not in song_list:
                    song_list.append(song_details)

            # scroll down
            current_pos = self.driver.execute_script("return window.pageYOffset;")
            ActionChains(self.driver).send_keys(Keys.PAGE_DOWN).perform()
            time.sleep(1)

            # click on show more button with Show More text
            try:
                show_more = self.driver.find_element(By.XPATH, "//*[contains(text(), 'Show More')]")
                show_more.click()
                time.sleep(2)
                

            except:
                songs = song_div.find_elements(By.XPATH, "//li[@data-testid='charts-entry-item']")
            
                for song in songs:
                    song_details = song.text.split('\n')
                                    
                    if song_details not in song_list:
                        song_list.append(song_details)
                
                break

        return song_list
