# this script extracts the data from https://www.minedu.gov.gr/covid19-schools.html

import pandas as pd


def extract_data():
    
    data = pd.read_json("https://covid19-schools.cti.gr/data/covid19-schools.json", encoding = 'utf-16')
    
    del data["RegistryNo"]
    
    data["DateFrom"] = data["DateFrom"].str.replace("\/", "-")
    data["DateTo"] = data["DateTo"].str.replace("\/", "-")
    data["Remarks"] = data["Remarks"].str.replace("\/", "-")

    with open('covid19-schools.json', 'w', encoding='utf-8') as file:
        data.to_json(file, orient ='records', indent = 3, force_ascii = False)

if __name__ == '__main__':
    extract_data()