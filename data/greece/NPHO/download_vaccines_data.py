import requests
import json
import pandas as pd
import sys

url = 'https://data.gov.gr/api/v1/query/mdg_emvolio'
auth_token = 'Token ' + str(sys.argv[1])

headers = {'Authorization': auth_token}
response = requests.get(url, headers = headers)

data = pd.DataFrame(response.json())

data = data.rename(columns = {'area': 'area_gr'})

data['referencedate'] = pd.to_datetime(data['referencedate'])

data.sort_values(by='referencedate')

data['referencedate'] = data['referencedate'].dt.strftime('%Y-%m-%d')

with open('vaccinations_data_history.json', 'w', encoding='utf-8') as file: 
    data.to_json(file, orient ='records', indent = 3, force_ascii = False)


area_ids = data['areaid'].unique()

idx = data.index
last_records = []

for area_id in area_ids:
    key = idx[data.areaid == area_id].tolist()[-1]
    last_records.append(data.iloc[key])

cum_per_area_data = pd.DataFrame(last_records)
cum_per_area_data = cum_per_area_data.drop(columns = ['daydiff', 'daytotal'])

with open('cumulative_per_area_vaccinations.json', 'w', encoding='utf-8') as file: 
    cum_per_area_data.to_json(file, orient ='records', indent = 3, force_ascii = False)

cum_data_dict = {
    'totaldistinctpersons': int(cum_per_area_data['totaldistinctpersons'].sum()),
    'totalvaccinations': int(cum_per_area_data['totalvaccinations'].sum()),
    'updated': cum_per_area_data['referencedate'].max()
}

cum_data = pd.DataFrame(cum_data_dict, index=[0])

with open('cumulative_vaccinations.json', 'w', encoding='utf-8') as file: 
    json.dump(cum_data_dict, file, indent = 3)