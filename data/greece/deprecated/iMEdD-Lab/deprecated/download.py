# this script downloads the data from iMEdD Lab

import os
import urllib.request
import sys

DOWNLOADS_DIR = './'

urls = ['https://raw.githubusercontent.com/iMEdD-Lab/open-data/master/COVID-19/greece.csv',
        'https://raw.githubusercontent.com/iMEdD-Lab/open-data/master/COVID-19/greeceTimeline.csv',
        'https://raw.githubusercontent.com/iMEdD-Lab/open-data/master/COVID-19/greece_cases.csv',
        'https://raw.githubusercontent.com/iMEdD-Lab/open-data/master/COVID-19/greece_deaths.csv']

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
