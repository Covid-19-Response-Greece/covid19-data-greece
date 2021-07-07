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


def extract_json():
    with open("regions_history_cases.csv", encoding="utf-8") as f:
        data_greece_regions_history = pd.read_csv(f)

    data_greece_regions_history = data_greece_regions_history.where(
        pd.notnull(data_greece_regions_history), None
    )

    date_list = list(data_greece_regions_history.columns[11:])
    tot_json = []
    # start_date = datetime.datetime.strptime('2/26/20', '%m/%d/%y')

    for idx, date in enumerate(date_list):

        transformed_date = datetime.strptime(date, "%m/%d/%y")
        # past_days_window = min(7, (transformed_date - start_date).days)
        # mean_cases_window = date_list[idx - past_days_window : idx +1]
        transformed_date = transformed_date.strftime("%Y-%m-%d")
        inner_json = []

        for i, row in data_greece_regions_history.iterrows():

            region_info = json.loads(
                row.iloc[0:9].to_json(orient="index", force_ascii=False)
            )
            region_cases = row.loc[date]
            region_info["cases"] = int(region_cases) if region_cases != None else None
            # diff_past_seven_days = np.diff(row[mean_cases_window]) if None not in list(row[mean_cases_window]) else []
            # mean_cases_past_seven_days = None
            # day_cases = None
            # if diff_past_seven_days != []:
            #     day_cases = diff_past_seven_days[-1]
            #     if np.sum(diff_past_seven_days) != 0:
            #         mean_cases_past_seven_days = np.mean(diff_past_seven_days)
            # region_info['mean_cases_past_seven_days'] = mean_cases_past_seven_days
            # region_info['cases_per_100000_people'] = round(day_cases / row['population']* 100000.0, 2) if (row['population'] != None and day_cases != None) else None
            inner_json.append(region_info)

        outer_json = {}
        outer_json["date"] = transformed_date
        outer_json["regions"] = inner_json
        tot_json.append(outer_json)

    with open("regions_history_cases.json", "w", encoding="utf-8") as f2:
        json.dump(tot_json, f2, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    download()
    process()
    extract_json()