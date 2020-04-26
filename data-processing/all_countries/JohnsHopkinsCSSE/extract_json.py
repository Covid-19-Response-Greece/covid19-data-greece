# this script converts the data from Johns Hopkins CSSE into a JSON file

import pandas as pd
import json

data_path = '../../../data/all_countries/JohnsHopkinsCSSE/'

def clean_data():
    print('Cleaning the data ...')

    conf_df = pd.read_csv(data_path + 'time_series_covid19_confirmed_global.csv', keep_default_na=False, na_values=[""])
    deaths_df = pd.read_csv(data_path + 'time_series_covid19_deaths_global.csv', keep_default_na=False, na_values=[""])
    recv_df = pd.read_csv(data_path + 'time_series_covid19_recovered_global.csv', keep_default_na=False, na_values=[""])

    dates = conf_df.columns[4:]

    conf_df_long = conf_df.melt(id_vars=['Province/State', 'Country/Region', 'Lat', 'Long'], \
        value_vars=dates, var_name='Date', value_name='Confirmed')

    deaths_df_long = deaths_df.melt(id_vars=['Province/State', 'Country/Region', 'Lat', 'Long'], \
        value_vars=dates, var_name='Date', value_name='Deaths')

    recv_df_long = recv_df.melt(id_vars=['Province/State', 'Country/Region', 'Lat', 'Long'], \
        value_vars=dates, var_name='Date', value_name='Recovered')

    table = pd.concat([conf_df_long, deaths_df_long['Deaths']], axis=1, sort=False)

    merge_keys = ['Province/State', 'Country/Region', 'Lat', 'Long', 'Date']
    table = pd.merge(left=table, right=recv_df_long, how='outer', left_on=merge_keys, right_on=merge_keys)

    # avoid double counting
    table = table[table['Province/State'].str.contains(',')!=True]

    # change Korea, South to South Korea
    table['Country/Region'] = table['Country/Region'].replace('Korea, South', 'South Korea')

    # sort by Date
    table['Date'] = pd.to_datetime(table['Date'])
    table = table.sort_values(by='Date')

    return table

def export_to_json(data, filename):
    json_output = '{'
    for name, group in data.groupby(["Country/Region"]):
        json_output += ('\n\t"' + name + '": [')
        for index, row in group.iterrows():
            json_output += '\n\t\t{\n\t\t\t'

            json_output += ('"date": "' + str(index[1])[:-9] + '",')
            json_output += ('\n\t\t\t"confirmed": ' + str(int(row['Confirmed'])) + ',')
            json_output += ('\n\t\t\t"recovered": ' + str(int(row['Recovered'])) + ',')
            json_output += ('\n\t\t\t"deaths": ' + str(int(row['Deaths'])))
            json_output += '\n\t\t},'

        json_output = json_output[:-1]
        json_output += '\n\t],'
    json_output = json_output[:-1]
    json_output += '\n}\n'


    with open(filename, 'w') as outfile:
        outfile.write(json_output)


if __name__ == '__main__':
    data = clean_data()

    data = data.drop(columns=["Province/State", "Lat", "Long"])

    data['Date'] = pd.to_datetime(data['Date'])
    data = data.groupby(["Country/Region", "Date"])["Confirmed", "Deaths", "Recovered"].sum()

    export_to_json(data, '../../../data/all_countries/JohnsHopkinsCSSE/cleaned-data/timeseries_per_country.json')
