import pandas as pd
import os

pd.set_option('display.max_colwidth', None)

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

def ceo_cleaner():
    df = pd.read_excel('data/csv/CEOs Pres and VPs.xlsx')
    df = df.rename(columns = {'Unnamed: 24': 'linkedin'})
    df = df.dropna(axis=1, how='all')

    # select rows the banks or Financial Services in the Industry column
    df = df[df['Industry'].str.contains("Bank|Financial Services", regex=True, na=False)]

    # drop duplicates in the Company Name column
    df = df.drop_duplicates(subset=['Company Name'], keep='first')
    
    # merge first name and second name, address and city, state, zip
    df['Exec_name'] = df[['First Name', 'Last Name']].apply(lambda row: ' '.join(row.values.astype(str)), axis=1)
    df['Address'] = df[['Address1', 'City', 'State', 'Zip']].apply(lambda row: ' '.join(row.values.astype(str)), axis=1)
    df = df.drop(['First Name', 'Last Name', 'Company Id', 'Employee Id', 'Address2', 'Ext', 'Fax', 'Revenue', 'Employees'], axis=1)
    df['Company URL'] = 'https://www.' + df['Company URL']
    bank_data = df[['Company Name', 'Company URL', 'Email', 'Address1', 'Main Phone', 'Exec_name', 'linkedin', 'Title', 'Address']]
    bank_data.reset_index(drop=True, inplace=True)
    
    # save the data to csv
    bank_data.to_csv("data/csv/bank_Pres_VPs.csv")

def us_bank_merged():
    df1 = pd.read_csv('data/csv/bank_Pres_VPs.csv')
    df2 = pd.read_csv('data/csv/us_banks.csv')

    company_names1 = df1['Company Name']
    company_names2 = df2['Company Name']

    company_names = pd.concat([company_names1, company_names2], ignore_index=True)
    company_names.drop_duplicates(inplace=True)
    company_names.reset_index(drop=True, inplace=True)

    print(company_names)
    
def eu_banks():
    df1 = pd.read_csv('data/csv/eu_banks.csv')
    
    # merge 'BOX', 'ADDRESS', 'POSTAL', 'CITY' into one column
    df1['Address'] = df1[['BOX', 'ADDRESS', 'POSTAL', 'CITY']].apply(lambda row: ' '.join(row.values.astype(str)), axis=1)
    df1 = df1.drop(['BOX', 'ADDRESS', 'POSTAL', 'CITY'], axis=1)
    df1.dropna(inplace=True, axis=1)

    # arrange the columns
    df1 = df1[['NAME', 'RIAD_CODE', 'COUNTRY_OF_REGISTRATION', 'Address']]
    print(df1.columns)

# eu_banks()
def crunchbasecos():
    df1 = pd.read_csv('data/csv/crunchbase organizations.csv')
    
    # get banks only from the short description if it contains the word bank or financial
    df1 = df1[df1['short_description'].str.contains("bank|financial|finance|banking|investment", regex=True, na=False)]

    df1 = df1[['name', 'type','cb_url', 'domain', 'homepage_url', 'facebook_url', 'twitter_url', 'linkedin_url', 'city', 'region', 'country_code',]]

    # create address column from city, region and country_code
    df1['Address'] = df1[['city', 'region', 'country_code']].apply(lambda row: ' '.join(row.values.astype(str)), axis=1)
    df1 = df1.drop(['city', 'region', 'country_code'], axis=1)

    # arrange the columns
    df1 = df1[['name', 'homepage_url', 'facebook_url', 'twitter_url', 'linkedin_url', 'Address']]

    df1 = df1.reset_index(drop=True)
    
    # save the data to csv
    df1.to_csv("data/csv/crunchbase_banks.csv")

crunchbasecos()