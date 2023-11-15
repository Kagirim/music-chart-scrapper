import requests
import pandas as pd
import re
import concurrent.futures
import threading
from bs4 import BeautifulSoup
import time
import json

class EdgarBareApi():
    def __init__(self):
        self.header = {
            'User-Agent': 'moorik morriskagiri@gmail.com'
        }
        self.base_url = 'https://data.sec.gov/api/xbrl'
        self.lock = threading.Lock()
        self.searched_bank_names = set()
        pd.set_option('display.max_colwidth', None)

    def get_ciks(self):
        url = 'https://www.sec.gov/Archives/edgar/cik-lookup-data.txt'
        ciks = requests.get(url, headers=self.header).text
        ciks = ciks.split('\n')
        ciks = list(map(lambda x: x.split(':'), ciks))
        ciks = pd.DataFrame(ciks)
        ciks = ciks.iloc[:, :2]
        ciks.columns = ['company_name', 'cik_str']
        # ciks.to_csv('banks/ciks.csv', index=False)
        
        return ciks

    def get_tickers(self):
        url = 'https://www.sec.gov/files/company_tickers.json'
        tickers = requests.get(url, headers=self.header).json()
        tickers = pd.DataFrame(tickers)
        tickers = tickers[['cik_str', 'ticker', 'title']]
        tickers.columns = ['cik_str', 'ticker', 'company_name']
        tickers = tickers.drop_duplicates()
        tickers = tickers.reset_index(drop=True)
        tickers.to_csv('banks/tickers.csv', index=False)

        return tickers

    def search_bank_cik(self, bank_names, ciks, start, end):
        for i in range(start, end):
            bank_name = bank_names.loc[i, 'company_name']
            with self.lock:
                if bank_name in self.searched_bank_names:
                    continue
                self.searched_bank_names.add(bank_name)

            cik = ciks[ciks['company_name'].str.contains(bank_name, regex=False, na=False)]
            if not cik.empty:
                bank_names.loc[i, 'cik_str'] = cik.iloc[0, 1]

                print(f'Found cik for {bank_name}')

    def get_bank_ciks(self):
        # get the bank names into a dataframe
        bank_names = pd.read_csv("institutions1.csv")
        bank_names['cik_str'] = ''
        bank_names.columns = ['company_name', 'cik_str']
        bank_names = bank_names.reset_index(drop=True)

        # get the ciks from the sec website
        ciks = self.get_ciks()
        ciks['cik_str'] = ciks['cik_str'].str.zfill(10)

        # Convert strings to lowercase
        bank_names['company_name'] = bank_names['company_name'].str.lower()
        ciks['company_name'] = ciks['company_name'].str.lower()

        # num_threads = 4
        # chunk_size = len(bank_names) // num_threads
        
        # # Create threads
        # threads = []
        # for i in range(num_threads):
        #     start = i * chunk_size
        #     end = (i + 1) * chunk_size if i < num_threads - 1 else len(bank_names)
        #     thread = threading.Thread(target=self.search_bank_cik, args=(bank_names, ciks, start, end))
        #     threads.append(thread)
        #     thread.start()

        # # Wait for all threads to finish
        # for thread in threads:
        #     thread.join()

        # get all company names with bank in the name
        banks = ciks[ciks['company_name'].str.contains('bank', regex=False, na=False)]
        banks = banks[['company_name', 'cik_str']]
        banks.columns = ['company_name', 'cik_str']

        # format the company names, removing trailing spaces and quotes
        banks['company_name'] = banks['company_name'].str.replace('"', '', regex=False)
        banks['company_name'] = banks['company_name'].str.replace("'", '', regex=False)
        banks['company_name'] = banks['company_name'].str.strip()

        # if there are multiple spaces in a row, or a comma, cut off the string from that point
        banks['company_name'] = banks['company_name'].str.split('  ').str[0]
        banks['company_name'] = banks['company_name'].str.split(',').str[0]

        # remove rows with duplicate company names even if the cik is different
        banks = banks.drop_duplicates(subset=['company_name'], keep='first')
        banks = banks.reset_index(drop=True)
        banks.to_csv('data/banks.csv', index=False)
        
    def get_submissions(self):
        url_endpoint = '/submissions'

        url = self.base_url + url_endpoint
        params = {
            'ciks': '0000102909',
            'date': '2020-12-31'
        }
        response = requests.get(url, params=params, headers=self.header)
        print(response.text)

    def get_company_facts(self):
        url_endpoint = '/companyfacts'

        url = self.base_url + url_endpoint
        banks = pd.read_csv('data/banks.csv')
        banks['cik_str'] = banks['cik_str'].str.zfill(10)
        banks = banks.iloc[0:1, :]
        for i in range(len(banks)):
            cik = banks.loc[i, 'cik_str']
            params = {
                'ciks': cik,
                'concept': 'Assets',
                'unit': 'USD',
                'date': '2020-12-31'
            }
            response = requests.get(f"{url}/CIK{cik}.json", params=params, headers=self.header)
            print(response.text)
            break

    def get_master_index_info(self):
        # open the master.idx file
        master_idx = open('data/master.idx', 'r')
        master_idx = master_idx.read()
        master_idx = master_idx.split('\n')
        columns = master_idx[9].split('|')
        master_idx = master_idx[11:]
        
        # create a dataframe with the data
        master_list = []
        for idx in master_idx:
            idx = idx.split('|')
            master_list.append(idx)

        master_df = pd.DataFrame(master_list)
        master_df.columns = columns
        
        # retain only 10-K and 10-Q filings
        master_df = master_df[master_df['Form Type'].isin(['DEF 14A'])]
        master_df['CIK'] = master_df['CIK'].str.zfill(10)

        # drop the date filed column
        master_df = master_df.drop(columns=['Date Filed'])

        # get the banks and merge with the master index on cik
        banks = pd.read_csv('data/csv/banks.csv')
        banks['cik_str'] = banks['cik_str'].str.zfill(10)
        banks = banks[['cik_str', 'company_name']]
        banks.columns = ['CIK', 'Bank Name']
        banks = banks.drop_duplicates(subset=['CIK'], keep='first')
        banks = banks.reset_index(drop=True)

        merged_df = pd.merge(master_df, banks, on='CIK', how='inner')
        
        # get the file names and append the https://www.sec.gov/Archives/ url prefix
        merged_df['Filename'] = 'https://www.sec.gov/Archives/' + merged_df['Filename']
        
        # for each file name, extract file contents
        files = merged_df['Filename'].tolist()
        location = []
        # for i, file in enumerate(files):
        #     file_content = requests.get(file, headers=self.header).text
        #     pattern = r"BUSINESS ADDRESS:\s+STREET 1:\s+(.*?)\s+STREET 2:\s+(.*?)\s+CITY:\s+(.*?)\s+STATE:\s+(.*?)\s+ZIP:\s+(.*?)\s+BUSINESS PHONE:\s+(.*?)\s"
        #     matches = re.findall(pattern, file_content, re.DOTALL)
        #     if matches:
        #         matches = matches[0]
        #         address = ' '.join(matches[:-2])
        #         phone = matches[-1]
        #         merged_df.loc[i, 'Address'] = address
        #         merged_df.loc[i, 'Phone'] = phone
                
        #         # location.append([address, phone])

            
        #     # wait for a fifth of a second
        #     time.sleep(0.2)
        #     break
        print(merged_df)

        
if __name__ == '__main__':
    edgarapi = EdgarBareApi()
    # edgarapi.get_bank_ciks()
    # edgarapi.get_company_facts()
    edgarapi.get_master_index_info()
    