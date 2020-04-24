# This script appends daily data from regions.json to cases_by_region_timeline.csv


import pandas as pd
from datetime import datetime


REGIONS_JSON_PATH = './regions.json'

CASES_BY_REGION_TIMELINE_CSV_PATH = './cases_by_region_timeline.csv'


def append_json_to_csv():
    
    timeline_df = pd.read_csv(CASES_BY_REGION_TIMELINE_CSV_PATH, encoding = 'utf8', header = 0)
    today = datetime.today().strftime('%d/%m/%Y')
    new_data = pd.read_json(REGIONS_JSON_PATH)
    new_data = new_data.drop('region_gr_name', axis = 1).rename(columns = {'region_cases': today}).set_index('region_en_name')
    if today not in timeline_df.columns:
        timeline_df = timeline_df.merge(new_data, left_on = 'Region', right_on = 'region_en_name', how = 'left')
    else:
        timeline_df = timeline_df.drop(today, axis = 1).merge(new_data, left_on = 'Region', right_on = 'region_en_name', how = 'left')
    
    return timeline_df.to_csv(CASES_BY_REGION_TIMELINE_CSV_PATH, index = False)

if __name__ == '__main__':
    append_json_to_csv()