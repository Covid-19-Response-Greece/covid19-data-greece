# This script downloads the data from https://www.ismood.com/

import os
import urllib.request
import sys
import json

DOWNLOADS_DIR = './'


headers = [#[('Referer', 'https://covid19live.ismood.com/'), ('Authorization', 'Basic ZmFkaWw6aXNjb3Y0NTZA',)],
           [('Referer', 'https://covid19live.ismood.com/'), ('Authorization', 'Basic ZmFkaWw6aXNjb3Y0NTZA',)],
           [('Referer', 'https://covid19live.ismood.com/'), ('Authorization', 'Basic ZmFkaWw6aXNjb3Y0NTZA',)]]

params = [#'?country_name=greece',
          '?country_name=greece',
          '?country_name=greece']

urls = [#'https://covidapi.ismood.com/total-info/',
        'https://covidapi.ismood.com/daily-info/',
        'https://covidapi.ismood.com/regions/']


def pretty_output_json(filename):
    
    with open(filename, encoding='utf8') as json_file:
        data = json.load(json_file)
    
    with open(filename, 'w', encoding='utf8') as outfile:
        json.dump(data, outfile, indent=4, sort_keys=True)

def download():
    print('Downloading data ...')

    if not os.path.exists(DOWNLOADS_DIR):
        os.makedirs(DOWNLOADS_DIR)

    for header, param, url in zip(headers, params, urls):
        
        name = url.rsplit('/', 2)[-2] + ".json"
        filename = os.path.join(DOWNLOADS_DIR, name)
        opener = urllib.request.build_opener()
        opener.addheaders = header
        urllib.request.install_opener(opener)
        total_url = url+param
        
        try:
            urllib.request.urlretrieve(total_url, filename)
            pretty_output_json(filename)

        except Exception as inst:
            print(inst)
            print('Encountered error')
            sys.exit()

    print('Done.')
    
if __name__ == '__main__':
    download()