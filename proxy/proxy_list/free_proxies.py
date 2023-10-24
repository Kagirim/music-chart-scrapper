import requests
from bs4 import BeautifulSoup
import pandas as pd
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.proxy import Proxy, ProxyType


def get_free_proxies():
    url = 'https://free-proxy-list.net/'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table', class_='table table-striped table-bordered')
    table_head = table.find('thead')
    table_body = table.find('tbody')

    headers = [th.text for th in table_head.find_all('th')]
    table_rows = table_body.find_all('tr')
    table_cells = [[td.text for td in row.find_all('td')] for row in table_rows]

    df = pd.DataFrame(table_cells, columns=headers)
    df = df.dropna()

    # create a dictionary of protocol: proxy addresses where https is 'yes' and https is 'no'
    proxy_servers = {'http': [], 'https': []}
    for index, row in df.iterrows():
        if row['Https'] == 'yes':
            proxy_servers['https'].append(f'{row["IP Address"]}:{row["Port"]}')

        elif row['Https'] == 'no':
            proxy_servers['http'].append(f'{row["IP Address"]}:{row["Port"]}')

    return proxy_servers


def proxy_request(translate_from='ko'):
    chrome_options = Options()

    # get the proxy servers
    proxy_servers = get_free_proxies()

    # rotate the proxy servers and try request until one works
    while True:
        random_https_proxy = random.choice(proxy_servers['https'])
        
        try:
            response = requests.get('https://www.google.com', proxies={'https': random_https_proxy})
            print("Proxy working: ", random_https_proxy)
            break
        
        except:
            print("Proxy not working: ", random_https_proxy)
            continue
        
    # create the driver with the proxy server
    proxy = Proxy(
        {
            'proxyType': ProxyType.MANUAL,
            'httpProxy': random_https_proxy,
            'httpsProxy': random_https_proxy,
            'noProxy': ''
        }
    )

    chrome_options.proxy = proxy

    # set the language preference from Korean to English
    prefs = {"translate_whitelists": {translate_from: "en"},
            "translate": {"enabled": "true"}}
    chrome_options.add_experimental_option("prefs", prefs)

    # set the user agent
    try:
        software_names = [SoftwareName.CHROME.value]

        operating_systems = [
            OperatingSystem.WINDOWS.value, 
            OperatingSystem.LINUX.value
        ]

        user_agent_rotator = UserAgent(
            software_names=software_names,
            operating_systems=operating_systems,
            limit=100
        )

        # Get list of user agents.
        user_agent = user_agent_rotator.get_user_agent()
        
        chrome_options.add_argument(f'user-agent={user_agent}')
    except:
        pass

    
    driver = webdriver.Chrome(options=chrome_options)

    return driver


if __name__ == '__main__':
    proxy_request()