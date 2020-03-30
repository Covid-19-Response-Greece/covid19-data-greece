# this script downloads the data from Johns Hopkins CSSE for all countries

import os
import urllib.request
import sys

DOWNLOADS_DIR = './data/'

urls = ['https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv',
        'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv',
        'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv']

def download():
    print('Downloading data ...')

    if not os.path.exists(DOWNLOADS_DIR):
        os.makedirs(DOWNLOADS_DIR)

    for url in urls:
        name = url.rsplit('/', 1)[-1]
        filename = os.path.join(DOWNLOADS_DIR, name)

        try:
            urllib.request.urlretrieve(url, filename)
        except Exception as inst:
            print(inst)
            print('Encountered error')
            sys.exit()

    print('Done.')

if __name__ == '__main__':
    download()
