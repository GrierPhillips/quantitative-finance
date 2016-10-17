#!/Users/Doedy/anaconda2/bin/python
import requests
import pandas as pd
from bs4 import BeautifulSoup

# Get wikipedia's list of S&P 500 equities table
source = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
r = requests.get(source)
html = r.text
soup = BeautifulSoup(html, 'html.parser')
table = soup.find(class_='wikitable sortable')

# Extract values from table

records = []
rows = table.findAll('tr')
for row in rows:
    cells = row.findAll('td')
    if cells:
        symbol = cells[0].string
        name = cells[1].string
        sector = cells[2].string
        records.append([symbol, name, sector])
s_p_500 = pd.DataFrame(records, columns=['Symbol', 'Name', 'Sector'])
s_p_500.to_csv('../Records/S&P_500_Equities.csv', index=False)
