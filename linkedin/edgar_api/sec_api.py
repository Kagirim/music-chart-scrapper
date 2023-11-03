"""
Using the SEC API (third party) to get the 10-K and 10-Q filings for a company

"""


class EDGARAPI():
    def __init__(self, api_key='44a0536407b35e878a979bb0839d6135ce7c71b79d5873258051eee913d540ad'):
        self.api_key = api_key

    def get_companies(self):
        mapping_api = MappingApi(self.api_key)
        nasdaq_companies = mapping_api.resolve('exchange', 'NASDAQ')
        nyse_companies = mapping_api.resolve('exchange', 'NYSE')

        nasdaq_banks = pd.DataFrame(nasdaq_companies)
        nyse_banks = pd.DataFrame(nyse_companies)

        banks = pd.concat([nasdaq_banks, nyse_banks])
        # check if the company is a bank
        bank1 = pd.read_csv('banks1.csv')
        banks = banks[banks['name'].isin(bank1['name'].tolist())]

        banks.to_csv('bank_tics.csv', index=False)
        
    def get_executive_names(self):
        exec_comp_api = ExecCompApi(self.api_key)
        
        # get tickers from csv file
        df = pd.read_csv('bank_tics.csv')
        tickers = df['ticker'].tolist()

        # get executive names
        query = {
            "query": {
                "query_string": {
                    "query": "ticker:({}) AND (year:2021 OR year:2020)".format(','.join(tickers))
                }
            },
            "from": 0,
            "size": 10000,
            "sort": [
                {
                    "total": {"order": "desc"}
                },
                {
                    "name.keyword": {"order": "asc"}
                }
            ]
        }
        result_query = exec_comp_api.get_data(query)

        senior_execs = list(map(lambda x: {
            "Ticker": x['ticker'],
            "Name": x['name'],
            "Position": x['position'],
            "Total": x['total'],
            "Year": x['year']
        }, result_query))

        
        # get only the top executive
        senior_execs = pd.DataFrame(senior_execs)
        senior_execs = senior_execs.sort_values(by=['Ticker', 'Total'], ascending=False)
        senior_execs = senior_execs.drop_duplicates(subset=['Ticker'], keep='first')
        senior_execs = senior_execs.to_dict('records')

        # append the company names respectively
        for i in range(0, len(senior_execs)):
            senior_execs[i]['Company'] = df[df['ticker'] == senior_execs[i]['Ticker']]['name'].values[0]

        # save to csv
        df = pd.DataFrame(senior_execs)
        df.to_csv('executive_compensation.csv', index=False)


    def get_insider(self):
        insider_api = InsiderTradingApi(self.api_key)

        # get tickers from csv file
        df = pd.read_csv('institutions1.csv')
        bank_names = df['NAME'].tolist()[:1000]
        bank_names = list(map(lambda x: x.lower(), bank_names))
        bank_names = list(set(bank_names))

        # group the bank names by 10
        bank_name_groups = [bank_names[i:i+10] for i in range(0, len(bank_names), 10)]

        # get insider transactions
        query = {
            "query": {
                "query_string": {
                    "query": ""
                }
            },
            "from": 1,
            "size": 10000,
            "sort": [
                {
                    "filedAt": {"order": "desc"}
                }
            ]
        }

        query_results = []
        for bank_name_group in bank_name_groups:
            try:
                query['query']['query_string']['query'] = "issuer.name:({})".format(','.join(bank_name_group))
                result_query = insider_api.get_data(query)
                query_results += result_query['transactions']

            except Exception as e:
                print(e)
                continue

        # save the results
        df = pd.DataFrame(query_results)
        df.to_csv('query_results.csv', index=False)

        # get only the top executive
        executives = list(map(lambda x: {
            "company": x['issuer']['name'],
            "executive": x['reportingOwner']['name']
        }, query_results))

        # save to csv                
        df = pd.DataFrame(executives)
        df.to_csv('execs.csv', index=False)