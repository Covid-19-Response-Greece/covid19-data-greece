# this script extracts data from Wikipedia and stores them in a .csv file

from bs4 import BeautifulSoup
import requests
import csv

URL = "https://el.wikipedia.org/wiki/%CE%A0%CE%B1%CE%BD%CE%B4%CE%B7%CE%BC%CE%AF%CE%B1_%CF%84%CE%BF%CF%85_%CE%BA%CE%BF%CF%81%CE%BF%CE%BD%CE%BF%CF%8A%CE%BF%CF%8D_%CF%83%CF%84%CE%B7%CE%BD_%CE%95%CE%BB%CE%BB%CE%AC%CE%B4%CE%B1_%CF%84%CE%BF_2020"

def filter_string(value):
    value = value.replace('\n', '')
    value = value.replace('.', '')

    if value == '':
        value = '0'

    value = value.replace('-', '')

    return value

def convert_greek_month_name_to_number(greek_month_name):

    months = {
        "Ιανουαρίου": "01",
        "Φεβρουαρίου": "02",
        "Μαρτίου": "03",
        "Απριλίου": "04",
        "Μαΐου": "05",
        "Ιουνίου": "06",
        "Ιουλίου": "07",
        "Αυγούστου": "08",
        "Σεπτεμβρίου": "09",
        "Οκτωβρίου": "10",
        "Νοεμβρίου": "11",
        "Δεκεμβρίου": "12"
    }

    month_number = months[greek_month_name]

    return month_number


def change_data_format(date_from_source):
    (day, month_name, year) = date_from_source.split()[:3]
    year = year.split("[",1)[0]
    
    month_number = convert_greek_month_name_to_number(month_name)

    if len(day) == 1:
        day = "0" + day

    new_date_format = year + "-" + month_number + "-" + day

    return new_date_format


def extract_table(soup):
    table = soup.find('table', { "class" : "wikitable sortable" })

    output_rows = []

    first_row = [
        'Date',
        'New confirmed cases',
        'New deaths',
        'Total recoveries',
        'In intensive care (total)',
        'Cumulative tests performed',
        'Active cases'
    ]

    output_rows.append(first_row)

    table_rows = table.findAll('tr')

    for i,table_row in enumerate(table_rows[1:-2]):


        if i == 98 :
            
            output_rows.append(['2020-06-03', '15', '1', '1442', '9', '193.929', '0'])
            output_rows.append(['2020-06-04', '15', '1', '1442', '9', '193.929', '0'])
            continue
        
        output_row = []
        date = table_row.find('th').text
        date = change_data_format(date)
        output_row.append(date)

        columns = table_row.findAll('td')

        for column in columns:
            output_row.append(filter_string(column.text))

        output_rows.append(output_row)

    last_row = ['Total']
    for cell in table_rows[-2].findAll('th')[1:]:
        last_row.append(filter_string(cell.text))

    output_rows.append(last_row)

    return output_rows

if __name__ == '__main__':
    content = requests.get(URL)
    soup = BeautifulSoup(content.text, 'html.parser')

    table_rows = extract_table(soup)

    with open('cases.csv', 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(table_rows)
