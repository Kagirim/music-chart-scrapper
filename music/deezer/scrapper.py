from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver import ActionChains
import time


class DeezerScrapper():
    def __init__(self, url, driver):
        self.url = url
        self.driver = driver
        self.driver.implicitly_wait(10)
        self.driver.get(self.url)

    def accept_cookies(self):
        get_btn = self.driver.find_element(By.XPATH, "//button[@id='gdpr-btn-accept-all']")
        return get_btn

    def login(self):
        email = ""
        password = ""
        self.driver.get(self.url)

        # wait for cookies to load
        WebDriverWait(self.driver, 10).until(expected_conditions.presence_of_element_located((By.XPATH, "//button[@id='gdpr-btn-accept-all']")))
        self.accept_cookies().click()
        time.sleep(1)

        # get the login form and enter email and password
        login_form = self.driver.find_element(By.XPATH, "//form[@id='login_form']")
        login_form.find_element(By.XPATH, "//input[@id='login_mail']").send_keys(email)
        time.sleep(1)
        login_form.find_element(By.XPATH, "//input[@id='login_password']").send_keys(password)
        time.sleep(1)
        login_form.find_element(By.XPATH, "//button[@id='login_form_submit']").click()


    def get_songs(self):
        # login to deezer
        # try:
        #     self.login()
        # except:
        #     print("problem logging in")
        # time.sleep(1)

        # wait and accept cookies
        WebDriverWait(self.driver, 10).until(expected_conditions.presence_of_element_located((By.XPATH, "//button[@id='gdpr-btn-accept-all']")))
        self.accept_cookies().click()
        time.sleep(1)

        # explore channels
        # WebDriverWait(self.driver, 50).until(
        #     expected_conditions.presence_of_element_located((By.XPATH, "//a[@data-tracking-action='data-tracking-action']"))
        #     ).click()

        # navigate to top 100 world
        world_wide_chart = self.driver.find_element(By.LINK_TEXT, "Top Worldwide")
        ActionChains(self.driver).scroll_by_amount(0, 200).perform()
        world_wide_chart.click()
        time.sleep(1)

        # scroll down the page while collecting songs
        songs = []
        song_indices = []
        table_div = self.driver.find_element(By.XPATH, "//div[@class='ZOZXb']")
        
        while True:
            song_divs = self.driver.find_elements(By.XPATH, "//div[@class='JR0qJ']")
            for song in song_divs:
                # get the song index
                try:
                    song_index = int(song.get_attribute("aria-rowindex"))
                except:
                    pass

                if song_index not in song_indices:
                     # get the song details
                    song_details = song.text.split("\n")

                    # check if there are multiple artists, merge them into one string and remove the extra items
                    if len(song_details) > 4:
                        song_details[1] = ", ".join(song_details[1:-2])
                        song_details = song_details[:2] + song_details[-2:]
                        
                    # add the song to the list
                    songs.append(song_details)
                    song_indices.append(song_index)

            # check the current position
            current_position = self.driver.execute_script("return window.pageYOffset;")

            # scroll down the page using page down key
            ActionChains(self.driver).send_keys(Keys.PAGE_DOWN).perform()
            time.sleep(1)

            # if clicking the page down key does not change the current position, break the loop
            if current_position == self.driver.execute_script("return window.pageYOffset;"):
                break
            
        return songs

            
            
