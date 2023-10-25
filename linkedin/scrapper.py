import os
import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv, find_dotenv
from pathlib import Path

# load the environment variables
load_dotenv(find_dotenv())


# create a class to scrape data from linkedin
class LinkedinScrapper():
    def __init__(self, search_url, driver):
        # define search url
        self.search_url = search_url
        self.driver = driver

    def connect(self):
        username = os.getenv('LINKEDIN_USER')
        password = os.getenv('LINKEDIN_PASSWORD')

        # open the linkedin login page
        self.driver.get('https://www.linkedin.com/login')
        time.sleep(1)

        # get the login form
        WebDriverWait(self.driver, 60).until(EC.presence_of_element_located((By.CLASS_NAME, 'login__form')))

        login_form = self.driver.find_element(By.CLASS_NAME, 'login__form')
        username_field = login_form.find_element(By.XPATH, "//input[@id='username']")
        time.sleep(1)
        username_field.send_keys(username)

        time.sleep(1)
        password_field = login_form.find_element(By.XPATH, "//input[@id='password']")
        time.sleep(1)
        password_field.send_keys(password)

        time.sleep(1)
        submit_button = login_form.find_element(By.XPATH, "//button[@aria-label='Sign in']")
        time.sleep(1)
        submit_button.click()
        
    def get_companies(self):
        # login if not logged in
        if self.driver.current_url != 'https://www.linkedin.com/feed/':
            self.connect()

        # open the search url
        self.driver.get(self.search_url)
        time.sleep(1)

        # get the companies
        WebDriverWait(self.driver, 60).until(EC.presence_of_element_located((By.XPATH, '//ul[@class="reusable-search__entity-result-list list-style-none"]')))
        company_list = self.driver.find_element(By.XPATH, '//ul[@class="reusable-search__entity-result-list list-style-none"]')
        time.sleep(1)

        # get company info
        company_list = []
        companies = company_list.find_elements(By.XPATH, '//li[@class="reusable-search__result-container"]')
        for company in companies:
            company_info = company.text.split('\n')
            company_list.append(company_info)

        return company_list