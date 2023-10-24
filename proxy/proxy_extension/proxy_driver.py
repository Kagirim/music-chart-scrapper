import os
import zipfile

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem


PROXY_HOST = 'p.webshare.io'  # rotating proxy or host
PROXY_PORT = 80 # port
PROXY_USER = 'jtdisvyh-rotate' # username
PROXY_PASS = '0fr2sk3jit9g' # password


manifest_json = """
{
    "version": "1.0.0",
    "manifest_version": 2,
    "name": "Chrome Proxy",
    "permissions": [
        "proxy",
        "tabs",
        "unlimitedStorage",
        "storage",
        "<all_urls>",
        "webRequest",
        "webRequestBlocking"
    ],
    "background": {
        "scripts": ["background.js"]
    },
    "minimum_chrome_version":"22.0.0"
}
"""

background_js = """
var config = {
        mode: "fixed_servers",
        rules: {
        singleProxy: {
            scheme: "http",
            host: "%s",
            port: parseInt(%s)
        },
        bypassList: ["localhost"]
        }
    };

chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

function callbackFn(details) {
    return {
        authCredentials: {
            username: "%s",
            password: "%s"
        }
    };
}

chrome.webRequest.onAuthRequired.addListener(
            callbackFn,
            {urls: ["<all_urls>"]},
            ['blocking']
);
""" % (PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASS)


def get_chromedriver():
    path = os.path.dirname(os.path.abspath(__file__))
    chrome_options = Options()

    # set the proxy extension
    pluginfile = 'proxy_auth_plugin.zip'
    with zipfile.ZipFile(pluginfile, 'w') as zp:
        zp.writestr("manifest.json", manifest_json)
        zp.writestr("background.js", background_js)

    chrome_options.add_extension(pluginfile)

    # set the language preference from Korean to English
    prefs = {"translate_whitelists": {"ko": "en"},
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
    get_chromedriver()