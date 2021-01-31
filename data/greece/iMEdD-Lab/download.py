# This script downloads greece regions data from iMEdD Lab

import os
import urllib.request
import sys
import pandas as pd
from datetime import datetime
import json


filenames = ["greece_cases_v2.csv", "greece_deaths_v2.csv", "greece_latest.csv"]
out_filenames = ['regions_history_cases.csv', 'regions_history_deaths.csv', 'regions_daily.csv']
DOWNLOADS_DIR = "./"

source_urls = [
    "https://raw.githubusercontent.com/iMEdD-Lab/open-data/master/COVID-19/greece_cases_v2.csv",
    "https://raw.githubusercontent.com/iMEdD-Lab/open-data/master/COVID-19/greece_deaths_v2.csv",
    "https://raw.githubusercontent.com/iMEdD-Lab/open-data/master/COVID-19/greece_latest.csv",
]


with open('regions_mapping.json', 'r', encoding="utf-8") as f:
    region_dict = json.load(f)

with open('areas_mapping.json', 'r', encoding="utf-8") as f:
    area_dict = json.load(f)

with open('geo_departments_mapping.json', 'r', encoding="utf-8") as f:
    geo_department_dict = json.load(f)

with open('regions_coordinates_mapping.json', 'r', encoding="utf-8") as f:
    region_coordinates_dict = json.load(f)


def download():

    print("Downloading data ...")

    if not os.path.exists(DOWNLOADS_DIR):
        os.makedirs(DOWNLOADS_DIR)

    for url in source_urls:

        name = url.rsplit("/", 1)[-1]
        filename = os.path.join(DOWNLOADS_DIR, name)

        try:
            urllib.request.urlretrieve(url, filename)
        except Exception as inst:
            print(inst)
            print("Encountered error")
            sys.exit()

def process():

    print("Processing data ...")
    last_updated_at = datetime.now().strftime('%Y-%m-%d')
    cumulative_cases_list = []
    cumulative_deaths_list = []
    for (file, out_file) in zip(filenames, out_filenames):

        with open(file, encoding = 'utf-8') as f:
        	file_pd = pd.read_csv(f, date_parser=lambda x: datetime.datetime.strptime(x, '%d/%m/%Y'), encoding="utf-8")

        file_pd = file_pd.where(pd.notnull(file_pd), None)
        file_pd = file_pd[(file_pd['county_normalized']!= "ΕΛΛΑΔΑ") & (file_pd['county_normalized']!= "ΚΡΟΥΑΖΙΕΡΟΠΛΟΙΟ") & (file_pd['Γεωγραφικό Διαμέρισμα']!= "Ελλάδα")]
        columns_count = len(file_pd.columns)
        region_data_df = pd.DataFrame(columns = ['area_gr', 'area_en', 'region_gr', 'region_en', 'geo_department_gr', 'geo_department_en', 'last_updated_at', 'longtitude', 'latitude' , 'population'] + list(file_pd.columns[5:]))
        if file == "greece_cases_v2.csv": cumulative_cases_list = list(file_pd.iloc[:, columns_count-1])
        if file == "greece_deaths_v2.csv": cumulative_deaths_list = list(file_pd.iloc[:, columns_count-1])

        for i, row in file_pd.iterrows():

            area_gr = row['county_normalized']
            area_en = area_dict[area_gr]
            region_gr = row['Περιφέρεια'].replace('Περιφέρεια ', '')
            region_en = region_dict[region_gr]
            geo_department_gr = row['Γεωγραφικό Διαμέρισμα']
            geo_department_en = geo_department_dict[geo_department_gr]
            longtitude = region_coordinates_dict[area_gr][0]
            latitude = region_coordinates_dict[area_gr][1]
            population = int(row['pop_11']) if row['pop_11'] != None else row['pop_11']
            incident_record_timeline = list(row.iloc[5:columns_count])
            region_data_entry = pd.Series([area_gr, area_en, region_gr, region_en, geo_department_gr, geo_department_en, last_updated_at, longtitude, latitude , population] + incident_record_timeline, index = region_data_df.columns)
            region_data_df = region_data_df.append(region_data_entry, ignore_index=True)

        if file == "greece_latest.csv":
            region_data_df = region_data_df.drop(['Πρωτεύουσα', 'county_normalized'], axis=1)
            temp_df = region_data_df
            temp_df = temp_df.rename(columns={'new_deaths':'total_deaths', 'new_cases':'total_cases'})
            temp_df['total_deaths'] = cumulative_deaths_list
            temp_df['total_cases'] = cumulative_cases_list
            temp_df.to_csv('regions_cumulative.csv', sep=',', encoding='utf-8', index=False)


        region_data_df.to_csv(out_file, sep=',', encoding='utf-8', index=False)
        os.remove(file)


if __name__ == "__main__":
    download()
    process()
