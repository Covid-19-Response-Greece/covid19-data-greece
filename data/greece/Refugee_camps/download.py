import os
import urllib.request
import sys

DOWNLOADS_DIR = './'

out_format = ['csv']
out_filename = ['refugee_camps']

source_url = ['https://docs.google.com/spreadsheets/d/1UeNgv7bpobAcL_3va67M4D38DSW_5YIwr77UmkqnWU0/gviz/tq?tqx=out:']

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