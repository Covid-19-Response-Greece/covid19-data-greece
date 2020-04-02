import io
from pathlib import Path
import tempfile
import zipfile

import requests
import numpy as np
import pandas as pd
import geopandas as gpd
import json

import datetime
from datetime import datetime as dt

from bokeh.io import curdoc, output_notebook, show, output_file
from bokeh.plotting import figure
from bokeh.models import GeoJSONDataSource, LinearColorMapper, ColorBar, HoverTool, DateSlider, FixedTicker
from bokeh.palettes import brewer
from bokeh.layouts import widgetbox, column


GREECE_PREFECTURE_BOUNDARY_FILE_URL = ('http://geodata.gov.gr/en/dataset/6deb6a12-1a54-41b4-b53b-6b36068b8348/'
                                        'resource/3e571f7f-42a4-4b49-8db0-311695d72fa3/download/nomoiokxe.zip')

GREECE_PREFECTURE_BOUNDARY_SHAPEFILE_PATH = Path('./nomoi_okxe/nomoi_okxe.shp')
DATA_GREECE_GEOGRAPHIC_DISTRIBUTION_PATH = Path('../data/greece/NPHO/geographic_distribution.csv')


DATE = ['2020_03_20',
        '2020_03_21',
        '2020_03_22',
        '2020_03_23',
        '2020_03_24',
        '2020_03_25',
        '2020_03_26',
        '2020_03_27',
        '2020_03_28',
        '2020_03_29'
        ]

GEOGRAPHIC_DISTRIBUTION_COLUMNS_MAP = {
    'Περιφερειακή ενότητα': 'prefecture',
    'Αριθμός κρουσμάτων': 'cases',
    'Ανά 100000 πληθυσμού': 'cases per 100,000 people'
    }

PREFECTURE_MAP = {
    'Άγιο Όρος': 'AGIO OROS',
    'Αθηνών': 'N. ATHINON',
    'Αιτωλοακαρνανίας': 'N. ETOLOAKARNANIAS',
    'Ανατολικής Αττικής': 'N. ANATOLIKIS ATTIKIS',
    'Αργολίδας': 'N. ARGOLIDAS',
    'Αρκαδίας': 'N. ARKADIAS',
    'Άρτας': 'N. ARTAS',
    'Αχαϊας': 'N. ACHAIAS',
    'Βοιωτίας': 'N. VIOTIAS',
    'Γρεβενών': 'N. GREVENON',
    'Δράμας': 'N. DRAMAS',
    'Δυτικής Αττικής': 'N. DYTIKIS ATTIKIS',
    'Δωδεκανήσου': 'N. DODEKANISON',
    'Έβρου': 'N. EVROU',
    'Εύβοιας': 'N. EVVIAS',
    'Ευρυτανίας': 'N. EVRYTANIAS',
    'Ζακύνθου': 'N. ZAKYNTHOU',
    'Ηλείας': 'N. ILIAS',
    'Ημαθίας': 'N. IMATHIAS',
    'Ηρακλείου': 'N. IRAKLIOU',
    'Θεσπρωτίας': 'N. THESPROTIAS',
    'Θεσσαλονίκης': 'N. THESSALONIKIS',
    'Ιωαννίνων': 'N. IOANNINON',
    'Καβάλας': 'N. KAVALAS',
    'Καρδίτσας': 'N. KARDITSAS',
    'Καστοριάς': 'N. KASTORIAS',
    'Κέρκυρας': 'N. KERKYRAS',
    'Κεφαλλονιάς': 'N. KEFALLONIAS',
    'Κιλκίς': 'N. KILKIS',
    'Κοζάνης': 'N. KOZANIS',
    'Κορινθίας': 'N. KORINTHOU',
    'Κυκλάδων': 'N. KYKLADON',
    'Λακωνίας': 'N. LAKONIAS',
    'Λαρίσης': 'N. LARISAS',
    'Λασιθίου': 'N. LASITHIOU',
    'Λέσβου': 'N. LESVOU',
    'Λευκάδας': 'N. LEFKADAS',
    'Μαγνησίας': 'N. MAGNISIAS',
    'Μεσσηνίας': 'N. MESSINIAS',
    'Ξάνθης': 'N. XANTHIS',
    'Πειραιώς': 'N. PIREOS KE NISON',
    'Πέλλας': 'N. PELLAS',
    'Πιερίας': 'N. PIERIAS',
    'Πρέβεζας': 'N. PREVEZAS',
    'Ρεθύμνου': 'N. RETHYMNOU',
    'Ροδόπης': 'N. RODOPIS',
    'Σάμου': 'N. SAMOU',
    'Σερρών': 'N. SERRON',
    'Τρικάλων': 'N. TRIKALON',
    'Φθιώτιδας': 'N. FTHIOTIDAS',
    'Φλώρινας': 'N. FLORINAS',
    'Φωκίδας': 'N. FOKIDAS',
    'Χαλκιδικής': 'N. CHALKIDIKIS',
    'Χανίων': 'N. CHANION',
    'Χίου': 'N. CHIOU',
    'Υπό διερεύνηση': 'UNDER INVESTIGATION'
    }


#Read shapefile using Geopandas
def read_greece_prefecture_boundary_shapefile():
    """Reads shape file of Greece prefecture boundaries from geodata.gov.
    Make sure to use requests_cache to cache the retrieved data.
    """
    r = requests.get(GREECE_PREFECTURE_BOUNDARY_FILE_URL)
    z = zipfile.ZipFile(io.BytesIO(r.content))
    with tempfile.TemporaryDirectory(prefix='greece-prefecture-boundary-files') as tmpdir:
        z.extractall(path = tmpdir)
        shape_file = Path(tmpdir) / GREECE_PREFECTURE_BOUNDARY_SHAPEFILE_PATH
        data = gpd.read_file(shape_file.as_posix())
        data = data[['NAME_ENG', 'geometry']]
    return data.rename(columns = {'NAME_ENG': 'prefecture'})
                          
greece_prefecture_boundary = read_greece_prefecture_boundary_shapefile()


#Read csv file using pandas
def create_geographic_distribution_df(datesList):
    data = pd.DataFrame()
    path_str = '../data/greece/NPHO/geographic_distribution_%s.csv'
    for date in datesList[:]:
        if Path(path_str %date).exists():
            temp = pd.read_csv((path_str %date), header = 0)
        else:
            temp = pd.read_csv((path_str %datesList[0]), header = 0, usecols = [list(GEOGRAPHIC_DISTRIBUTION_COLUMNS_MAP.keys())[0]])
        temp.insert(1, 'date', date)
        data = data.append(temp)
    data = data.rename(columns = GEOGRAPHIC_DISTRIBUTION_COLUMNS_MAP)
    data = data.set_index('prefecture').rename(index = PREFECTURE_MAP)
    return data.reset_index()

data_greece_geographic_distribution = create_geographic_distribution_df(DATE)


#Define function that returns json_data for date selected by user.  
def json_data(selectedDate):
    #Filter data for selected date.
    data = data_greece_geographic_distribution
    data_date = data[data['date'] == selectedDate]
    #Merge dataframes greece_prefecture_boundary and data_date, preserving every row in the former via left-merge.
    merged = greece_prefecture_boundary.merge(data_date, left_on = 'prefecture', right_on = 'prefecture', how = 'left')
    #Replace NaN values to string 'No data'.
    merged.fillna({'date': selectedDate, 'cases': 'No data', 'cases per 100,000 people': 'No data'}, inplace = True)
    #Read data to json.
    merged_json = json.loads(merged.to_json())
    #Convert to String like object.
    json_data = json.dumps(merged_json)
    return json_data

#Input GeoJSON source that contains features for plotting.
geosource = GeoJSONDataSource(geojson = json_data(DATE[-1]))


#Define a sequential multi-hue color palette and reverse order so that dark => high # of cases.
palette = brewer['YlOrRd'][8]
palette = palette[::-1]

#Transform palette to create non-uniform intervals
base_colors = palette
bounds = [-100000, 0, 10, 20, 50, 100, 200, 400, 800, 100000]
low = 0
high = 800
bound_colors = []
j = 0
for i in range(low, high, 10):
    if i >= bounds[j+1]:
        j += 1
    bound_colors.append(base_colors[j])
    
#Instantiate LinearColorMapper that linearly maps numbers in a range, into a sequence of colors. Input nan_color.
color_mapper = LinearColorMapper(palette = bound_colors, low = low, high = high, nan_color = '#d9d9d9')

#Add hover tool.
hover = HoverTool(tooltips = [('prefecture', '@prefecture'), ('# of cases', '@cases')])

#Define custome ticks for colorbar.
ticks = np.array([0, 20, 50, 100, 200, 400, 800])

#Create color bar. 
color_bar = ColorBar(color_mapper = color_mapper, label_standoff = 8, width = 800, height = 20,border_line_color= None,
                     location = (0,0), orientation = 'horizontal', ticker = FixedTicker(ticks = ticks))

#Create figure object.
p = figure(title = 'COVID-19 cases in Greece, %s' %DATE[-1], 
           plot_height = 600 , plot_width = 950, toolbar_location = None, tools = [hover])
p.xgrid.grid_line_color = None
p.ygrid.grid_line_color = None

#Add patch renderer to figure. 
p.patches('xs','ys', source = geosource, fill_color = {'field' :'cases', 'transform' : color_mapper},
          line_color = 'black', line_width = 0.25, fill_alpha = 1)

#Specify figure layout.
p.add_layout(color_bar, 'below')

# Define the callback function: update_plot
def update_plot(attr, old, new):
    date = dt.utcfromtimestamp(slider.value/1000).strftime('%Y_%m_%d')
    #date = DATE[slider.value]
    new_data = json_data(date)
    geosource.geojson = new_data
    p.title.text = 'COVID-19 cases in Greece, %s' %date
    
#Make a slider object: slider 
slider = DateSlider(title = 'Date',
                    start = dt.strptime(DATE[0], '%Y_%m_%d'),
                    end = dt.strptime(DATE[-1], '%Y_%m_%d'),
                    #step = 1,
                    step = int(datetime.timedelta(days = 1).total_seconds()*1000), 
                    value = dt.strptime(DATE[-1], '%Y_%m_%d')
                    )
slider.on_change('value', update_plot)

#Make a column layout of widgetbox(slider) and plot, and add it to the current document
layout = column(p,widgetbox(slider))
curdoc().add_root(layout)

#Display on Localhost. Type following commands in cmd.
# cd Documents/GitHub/covid19-data-greece/analysis (for my pc only)
# bokeh serve --show choropleth_interactive.py

