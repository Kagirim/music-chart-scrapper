from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import time


def scroller(driver, current_position):
    while current_position <= driver.execute_script("return window.pageYOffset;"):
        # scroll down the page using page down key
        ActionChains(driver).send_keys(Keys.PAGE_DOWN).perform()
        time.sleep(1)

    return driver