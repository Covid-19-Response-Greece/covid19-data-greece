import io
from pathlib import Path
import tempfile
import zipfile

import requests
import pandas as pd
import geopandas as gpd
#import geoplot as gplt
import matplotlib.pyplot as plt
import seaborn as sns


GREECE_PREFECTURE_BOUNDARY_FILE_URL = ('http://geodata.gov.gr/en/dataset/6deb6a12-1a54-41b4-b53b-6b36068b8348/'
                                        'resource/3e571f7f-42a4-4b49-8db0-311695d72fa3/download/nomoiokxe.zip')

GREECE_PREFECTURE_BOUNDARY_SHAPEFILE_PATH = Path('./nomoi_okxe/nomoi_okxe.shp')
DATA_GREECE_GEOGRAPHIC_DISTRIBUTION_PATH = Path('./data/greece/NPHO/geographic_distribution.csv')


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
    'Υπό διευρεύνηση': 'UNDER INVESTIGATION'
    }


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
        
    return data.set_index('NAME_ENG').rename_axis('prefecture')

                          
greece_prefecture_boundary = read_greece_prefecture_boundary_shapefile()

data_greece_geographic_distribution = pd.read_csv(DATA_GREECE_GEOGRAPHIC_DISTRIBUTION_PATH, header = 0)
data_greece_geographic_distribution = data_greece_geographic_distribution.rename(columns = GEOGRAPHIC_DISTRIBUTION_COLUMNS_MAP)
data_greece_geographic_distribution = data_greece_geographic_distribution.set_index('prefecture').rename(index = PREFECTURE_MAP)

geo_data = greece_prefecture_boundary.join(data_greece_geographic_distribution)
geo_data.fillna({'cases': 0, 'cases per 100,000 people': 0}, inplace = True)


def plot_choropleth(geo_data, column, path_to_choropleth):
    sns.set_context('poster')
    fig, ax = plt.subplots(1, figsize = (10, 6))
    geo_data.plot(
        column = column,
        categorical = False,
        linewidth = 0.2,
        legend = True,
        cmap = 'viridis',
        edgecolor = '0.8',
        ax = ax
    )
    ax.set_aspect(1)
    _ = plt.xticks([])
    _ = plt.yticks([])
    ax.set_title('COVID-19: \n ' + column + ' \n in Greece', fontdict = {'fontsize': '15', 'fontweight': '1'})
    
    fig.savefig(path_to_choropleth, dpi = 300)
    sns.set_context('paper')


path_to_choropleth_plot_1 = Path('./data/greece/NPHO/geographic_distribution_choropleth_1.png')
path_to_choropleth_plot_2 = Path('./data/greece/NPHO/geographic_distribution_choropleth_2.png')    
plot_choropleth(geo_data, 'cases', path_to_choropleth_plot_1)
plot_choropleth(geo_data, 'cases per 100,000 people', path_to_choropleth_plot_2)

