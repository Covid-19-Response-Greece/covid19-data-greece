# this script extracts data from https://www.sch.gr/anastoli/web/index.php and stores them in a .csv file

from bs4 import BeautifulSoup
import requests
import csv
import datetime
import re

URL = "https://www.sch.gr/anastoli/web/index.php"


def extract_table(soup):
    table = soup.find('table', { "class" : "kv-grid-table table table-bordered table-striped kv-table-wrap" })

    table_rows = table.findAll('tr')

    headers = table.findAll('th')

    first_row = []

    for header in headers:
        first_row.append(header.text)

    output_rows = []
    output_rows.append(first_row)

    for table_row in table_rows:
        
        output_row = []
        
        columns = table_row.findAll('td')

        for column in columns:

            value = column.text 

            if value == '':
                value = '-'
            if value == '-':
                value = ''
            output_row.append(value)
        
            
        output_rows.append(output_row)

    output_rows.pop(1)
    output_rows.pop(1)

    return output_rows

if __name__ == '__main__':
    content = requests.get(URL)
    soup = BeautifulSoup(content.text, 'html.parser')

    table_rows = extract_table(soup)

    with open('schools_status.csv', 'w', encoding = 'utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(table_rows)
