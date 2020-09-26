# this script extracts data from https://www.sch.gr/anastoli/web/index.php and stores them in a .csv file

from bs4 import BeautifulSoup
import requests
import csv
import datetime
import re

URL = "https://www.sch.gr/anastoli/web/index.php?r=site%2Findex&page="


def extract_table(soup):

    summary = soup.find('div', {"class" : "summary"}).findAll('b')

    elements_range = summary[0]
    last_displayed_element = elements_range.text.split("-",1)[1]
    last_element = summary[1].text

    is_last_page = False 

    if last_displayed_element == last_element:
        is_last_page = True

    table = soup.find('table', { "class" : "kv-grid-table table table-hover table-bordered table-striped table-condensed kv-table-wrap" })

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

    return output_rows, is_last_page

if __name__ == '__main__':

    page_index = 1 

    table_rows = []

    while True:

        content = requests.get(URL + str(page_index))
        soup = BeautifulSoup(content.text, 'html.parser')

        result_table, is_last_page = extract_table(soup)
        

        if page_index > 1:
            result_table.pop(0)

        table_rows.extend(result_table)

        if is_last_page:
            break 

        page_index += 1


    with open('schools_status.csv', 'w', encoding = 'utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(table_rows)
