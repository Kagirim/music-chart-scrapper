import requests
# import bankfind as bf
import pandas as pd
from secedgar import CompanyFilings, FilingType, filings
from secedgar.cik_lookup import CIKLookup
from sec_edgar_downloader import Downloader
from get_all_tickers import get_tickers as gt


bank_tickers = gt.get_tickers()
print(bank_tickers)


def get_institutions():
    institution_data = []
    institutions = bf.get_institutions()
    for i in range(0, len(institutions['data'])):
        try:
            name = institutions['data'][i]['NAME']

        except:
            name = ''
            
        try:
            ticker = institutions['data'][i]['CERT']

        except:
            ticker = ''

        try:
            web = institutions['data'][i]['WEBADDR']
        except:
            web = ''

        try:
            address = institutions['data'][i]['ADDRESS']

        except:
            address = ''

        institution_data.append([name, web])

    return institution_data


def get_locations():
    location_data = []
    locations = bf.get_locations()
    for i in range(0, len(locations['data'])):
        try:
            name = locations['data'][i]['NAME']
        except:
            name = ''

        try:
            address = locations['data'][i]['ADDRESS']

        except:
            address = ''
            
        location_data.append([name, address])

    return location_data