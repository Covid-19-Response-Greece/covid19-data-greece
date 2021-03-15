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

from bokeh.io import curdoc
from bokeh.plotting import figure, save
from bokeh.models import GeoJSONDataSource, LinearColorMapper, ColorBar, HoverTool, DateSlider, FixedTicker
from bokeh.palettes import brewer
from bokeh.layouts import column


OUTPUT_FILE_PATH = '../../visualizations/geographic_distribution_greece_2020_03_29.html'

PREFECTURE_BOUNDARIES_FILE_URL = ('http://geodata.gov.gr/en/dataset/6deb6a12-1a54-41b4-b53b-6b36068b8348/'
                                  'resource/3e571f7f-42a4-4b49-8db0-311695d72fa3/download/nomoiokxe.zip')

PREFECTURE_BOUNDARIES_SHAPEFILE_PATH = './nomoi_okxe/nomoi_okxe.shp'

GEOGRAPHIC_DISTRIBUTION_DATA_PATH = '../../data/greece/NPHO/geographic_distribution_%s.csv'

DATES = [
    '2020_03_20',
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


def create_interactive_map():
    prefecture_boundaries = _read_prefecture_boundaries_shapefile()
    geographic_distribution_data = _read_geographic_distribution_data(DATES)
    geo_source = GeoJSONDataSource(geojson = _merge_and_convert_to_json(prefecture_boundaries, geographic_distribution_data, DATES[-1]))
    _plot_choropleth(geo_source, prefecture_boundaries, geographic_distribution_data)


def _read_prefecture_boundaries_shapefile():
    """Reads shape file of Greece prefecture boundaries from geodata.gov.
    """
    r = requests.get(PREFECTURE_BOUNDARIES_FILE_URL)
    z = zipfile.ZipFile(io.BytesIO(r.content))
    with tempfile.TemporaryDirectory(prefix='greece-prefecture-boundary-files') as tmpdir:
        z.extractall(path = tmpdir)
        shape_file = Path(tmpdir) / PREFECTURE_BOUNDARIES_SHAPEFILE_PATH
        data = gpd.read_file(shape_file.as_posix())
        data = data[['NAME_ENG', 'geometry']]
    return data.rename(columns = {'NAME_ENG': 'prefecture'})
                          

def _read_geographic_distribution_data(datesList):
    """Reads data for the geographic distribution of COVID-19 cases in Greece
    from csv files for the dates in DATES.
    """
    data = pd.DataFrame()
    path_str = GEOGRAPHIC_DISTRIBUTION_DATA_PATH
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


def _merge_and_convert_to_json(prefectureBoundaries, geographicDistributionData, selectedDate):
    """Merges the prefecture_boundaries geoDataFrame with the geographic_distribution Dataframe
    and converts them to a JSON string, to be passed to GeoJSONDataSource,
    so that they can be used as data source for the choropleth plot.
    """
    data = geographicDistributionData
    
    #Filter data for selected date.
    data_date = data[data['date'] == selectedDate]
    
    #Merge dataframes prefecture_boundaries and data_date, preserving every row in the former via left-merge.
    merged = prefectureBoundaries.merge(data_date, left_on = 'prefecture', right_on = 'prefecture', how = 'left')
    
    #Replace NaN values with string 'No data' and add date where missing.
    merged.fillna({'date': selectedDate, 'cases': 'No data', 'cases per 100,000 people': 'No data'}, inplace = True)
    
    #Read data to json.
    merged_json = json.loads(merged.to_json())
    
    #Convert to String like object.
    json_data = json.dumps(merged_json)
    return json_data


def _transform_color_intervals(baseColors, low, high):
    """Transforms a color palette to create non-uniform intervals
    with LinearColorMapper.
    """
    bounds = [-100000, 0, 10, 20, 50, 100, 200, 400, 800, 100000]
    step = min(abs(bounds[i]-bounds[i-1]) for i in range(len(bounds)))
    bound_colors = []
    j = 0
    for i in range(low, high, step):
        if i >= bounds[j+1]:
            j += 1
        bound_colors.append(baseColors[j])
    return bound_colors, low, high


def _plot_choropleth(geoSource, prefectureBoundaries, geographicDistributionData):
    #Define a sequential multi-hue color palette and reverse order so that dark => high # of cases.
    base_colors = brewer['YlOrRd'][8]
    base_colors = base_colors[::-1]
    
    #Transform palette to create non-uniform intervals.
    palette, low, high = _transform_color_intervals(base_colors, 0, 800)

    #Instantiate LinearColorMapper that maps numbers in a range, into a sequence of colors. Input nan_color.
    color_mapper = LinearColorMapper(palette = palette, low = low, high = high, nan_color = '#d9d9d9')

    #Add hover tool.
    hover = HoverTool(tooltips = [('prefecture', '@prefecture'), ('# of cases', '@cases')])

    #Define custom ticks for colorbar.
    ticks = np.array([0, 20, 50, 100, 200, 400, 800])

    #Create color bar. 
    color_bar = ColorBar(color_mapper = color_mapper, label_standoff = 8, width = 800, height = 20,border_line_color= None,
                         location = (0,0), orientation = 'horizontal', ticker = FixedTicker(ticks = ticks))

    #Create figure object.
    p = figure(title = 'COVID-19 cases in Greece, %s' %DATES[-1], 
               plot_height = 600 , plot_width = 950, toolbar_location = None, tools = [hover])
    p.xgrid.grid_line_color = None
    p.ygrid.grid_line_color = None

    #Add patch renderer to figure. 
    p.patches('xs','ys', source = geoSource, fill_color = {'field' :'cases', 'transform' : color_mapper},
              line_color = 'black', line_width = 0.25, fill_alpha = 1)

    #Specify figure layout.
    p.add_layout(color_bar, 'below')
    
    def _update_plot(attr, old, new):
        """Callback function to update the plot using a slider.
        """
        date = dt.utcfromtimestamp(slider.value/1000).strftime('%Y_%m_%d')
        new_data = _merge_and_convert_to_json(prefectureBoundaries, geographicDistributionData, date)
        geoSource.geojson = new_data
        p.title.text = 'COVID-19 cases in Greece, %s' %date

    #Make a slider object to trigger _update_plot.
    slider = DateSlider(title = 'Date',
                        start = dt.strptime(DATES[0], '%Y_%m_%d'),
                        end = dt.strptime(DATES[-1], '%Y_%m_%d'),
                        step = int(datetime.timedelta(days = 1).total_seconds()*1000), 
                        value = dt.strptime(DATES[-1], '%Y_%m_%d')
                        )
    slider.on_change('value', _update_plot)

    #Make a column layout of plot and slider, and add it to the current document.
    layout = column(p, column(slider))
    curdoc().add_root(layout)
    curdoc().title = 'COVID-19 cases in Greece'
    
    #Crete an HTML of the static choropleth for 2020-03-29.
    save(p, OUTPUT_FILE_PATH, resources = None, title = 'COVID-19 cases in Greece, 2020_03_29')
    
    
create_interactive_map()
    
#To display the interactive map on Localhost, type the following in cmd.
# bokeh serve --show choropleth_interactive.py

