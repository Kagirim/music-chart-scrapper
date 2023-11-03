import requests
import pandas as pd


class EdgarBareApi():
    def __init__(self):
        self.header = {
            'User-Agent': 'morriskagiri@gmail.com'
        }
        self.base_url = 'https://data.sec.gov/api/xbrl'

    def get_ciks(self):
        url = 'https://www.sec.gov/Archives/edgar/cik-lookup-data.txt'
        ciks = requests.get(url, headers=self.header).text
        ciks = ciks.split('\n')
        ciks = list(map(lambda x: x.split(':'), ciks))
        ciks = pd.DataFrame(ciks)

        ciks.columns = ['cik_str', 'name', 'ticker']
        ciks.to_csv('ciks.csv', index=False)
        print(ciks)
        return ciks

    def get_company_facts(self):
        url = '{}/companies.json'.format(self.base_url)

    def get_company_info(self):
        # get the bank tickers
        df = pd.read_csv('institutions1.csv')
        bank_names = df['NAME'].tolist()
        bank_names = list(map(lambda x: x.lower(), bank_names))
        bank_names = list(set(bank_names))

        # get the cik numbers
        cik_numbers = self.tickers[self.tickers['ticker'].isin(bank_names)]['cik_str'].tolist()

        # get the company info
        company_info = []
        for cik_number in cik_numbers:
            try:
                url = 'https://data.sec.gov/api/xbrl/companyfacts/CIK{}/Facts'.format(cik_number)
                company_info.append(requests.get(url, headers=self.header).json())

            except Exception as e:
                print(e)
                continue

        # save the results
        df = pd.DataFrame(company_info)
        df.to_csv('company_info.csv', index=False)

        # get the executive names
        executives = []
        for company in company_info:
            try:
                executives.append(company['facts']['EntityRegistrantName'])

            except Exception as e:
                print(e)
                continue

        # save the results
        df = pd.DataFrame(executives)
        df.to_csv('execs10.csv', index=False)

    
  
edgarapi = EdgarBareApi()
# edgarapi.get_ciks()