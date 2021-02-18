import os
import urllib.request
import sys

DOWNLOADS_DIR = './'

out_format = ['csv', 'csv']
out_filename = ['western_macedonia_daily_reports', 'western_macedonia_deaths']

source_url = ['https://docs.google.com/spreadsheets/d/19sfozGXRp7uOuVl-cgjNzeqi-Sx64PMo6vxoZtdCmIQ/gviz/tq?tqx=out:',
              'https://docs.google.com/spreadsheets/d/1uUECU0vTQYuZpFIL4-v-tOtbz1a2C4WQAnwStzU1BBY/gviz/tq?tqx=out:']


print('Downloading data ...')

for i in range(len(out_filename)):
    
    filename = os.path.join(DOWNLOADS_DIR, out_filename[i] + '.' + out_format[i])
    
    try:
        urllib.request.urlretrieve(source_url[i] + out_format[i] + '&sheet=' + out_filename[i], filename)
    except Exception as inst:
        print(inst)
        print('Encountered error')
        sys.exit()

print('Done.')