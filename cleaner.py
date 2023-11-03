import pandas as pd
import os

def cleaner():
    bank_data = pd.read_csv('bank_data.csv')
    execs = pd.read_csv('execs.csv')

    # clean bank_data
    bank_data['name'] = bank_data['name'].str.lower()
    bank_data = bank_data.dropna()
    bank_data = bank_data.drop_duplicates()

    execs = execs.dropna()
    execs = execs.drop_duplicates()
    execs['company'] = execs['company'].str.lower()
    execs['company'] = execs['company'].str.replace('inc', '')
    execs['company'] = execs['company'].str.replace('.', '')
    execs['company'] = execs['company'].str.replace(',', '')
    execs['company'] = execs['company'].replace('"', '').str.strip()

    # check the company name in the execs df and if it contains the bank_data name, then append the executive to that  bank_data row
    # for index, row in bank_data.iterrows():
    #     bank_name = row['name']
    #     bank_data.at[index, 'execs'] = execs[execs['company'].str.contains(row['name'], regex=False, na=False)]['company'].tolist()
    
    emails = pd.read_excel('emails_of_bankers.xlsx')
    emails.columns = ['executive', 'email1', 'email2', 'bank']
    emails['bank'] = emails['bank'].str.replace(r'\(.*\)', '', regex=True)
    emails = emails.drop_duplicates(subset=['bank'])
    emails['bank'] = emails['bank'].str.lower()
    emails['bank'] = emails['bank'].str.replace('inc', '')
    emails['bank'] = emails['bank'].str.replace('.', '').str.replace(',', '').str.replace('"', '').str.strip()
    emails.reset_index(drop=True, inplace=True)

    # rearrange the columns
    emails = emails.reindex(columns=['bank', 'executive', 'email1', 'email2'])

    # get the bank names from the bank_names.xlsx file
    bank_names = pd.read_excel('bank_names.xlsx')
    bank_names.columns = bank_names.iloc[0]
    bank_names = bank_names[1:]

    bank_names['Company Name'] = bank_names['Company Name'].str.replace(r'\(.*\)', '', regex=True)
    bank_names['Company Name'] = bank_names['Company Name'].str.lower()
    bank_names['Company Name'] = bank_names['Company Name'].str.replace('inc', '')
    bank_names['Company Name'] = bank_names['Company Name'].str.replace('.', '').str.replace(',', '').str.replace('"', '').str.strip()

    # get the address and phone separately
    bank_names['Primary Address'] = bank_names['Primary Address'].str.split('\n')

    # split the address and phone into separate columns
    bank_names['Address'] = bank_names['Primary Address'].apply(lambda x: x[1:-1])
    bank_names['Phone'] = bank_names['Primary Address'].apply(lambda x: x[-1])
    bank_names['Phone'] = bank_names['Phone'].str.replace('Main Phone: ', '')
    bank_names['Phone'] = bank_names['Phone'].str.replace('Main Fax: ', '')

    # drop email2 column
    emails = emails.drop(columns=['email2'])

    # drop the primary address column
    bank_names = bank_names.drop(columns=['Primary Address'])

    # merge the emails and bank_names
    bank_names = bank_names.merge(emails, left_on='Company Name', right_on='bank', how='left')

    # extract the website url from the email1 column by removing username and @ symbol and replace with www.
    bank_names['Website'] = bank_names['email1'].str.replace(r'.*@', 'www.', regex=True)
    bank_names['Website'] = bank_names['Website'].str.replace(r'www.www.', 'www.', regex=True)

    # if the website url is not available, then use the bank name to create the url
    bank_names['Website'] = bank_names['Website'].fillna(bank_names['Company Name'].str.replace(' ', '').str.lower() + '.com')

    # rename email1 column name
    bank_names = bank_names.rename(columns={'email1': 'Email'})

    bank_names.to_csv('us_banks.csv', index=False)
    
    # # print(emails)
    print(bank_names)
    # print(emails)

def cleaner2():
    bank_data = pd.read_csv('bank_data.csv')

    # remove duplicates at name column, retain the first
    bank_data = bank_data.drop_duplicates(subset=['name'], keep='first')
    
    all_data = pd.read_csv('query_results.csv')

    # drop the first three and last three columns
    all_data = all_data[['issuer', 'reportingOwner', 'nonDerivativeTable', 'ownerSignatureName', 'ownerSignatureNameDate', 'footnotes', 'derivativeTable']]
    
    # extract the issuer column, split and extract the name
    all_data['issuer'] = all_data['issuer'].str.split(',')
    all_data['issuer'] = all_data['issuer'].apply(lambda x: x[0].split(':'))
    all_data['issuer'] = all_data['issuer'].apply(lambda x: x[1])

    # extract the reportingOwner column, split and extract the name
    # all_data['reportingOwner'] = all_data['reportingOwner'].str.split(',')
    print(all_data['issuer'])
    
    # issuer column contains the objects, convert to json and extract the name from issuer and from reportingOwner


    # print(all_data)

cleaner2()