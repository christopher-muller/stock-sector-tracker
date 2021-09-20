from bs4 import BeautifulSoup
import requests
import mysql.connector
from datetime import date

db = mysql.connector.connect(
    host="Insert MySQL info here",
    user="Insert MySQL info here",
    passwd="Insert MySQL info here",
    database="Insert MySQL info here"
    )

url = "https://csimarket.com/screening/performance.php"
result = requests.get(url)
doc = BeautifulSoup(result.text, "html.parser")

# Gather the text elements that display the percent increases of each sector (identifiable by their class: scrimeutabl12 sivi)
prices = doc.find_all("td", class_="scrimeutab12 sivi")

# 16 is used because only every other scrimeutabl12 sivi element is an actual percent increase, and there are 8 sectors
# ie. prices is formated like [1, 2.94%, 2, 3.92%, etc...]
numbers = []
for i in range(16):
    if i % 2 == 1:
        # parse the numerical percent increase from the % for each element and add to a list
        for char in prices[i].text.split():
            if char != "%":
                numbers.append(float(char))


# find leading sector
sectors = ["Consumer Non Cyclical", "HealthCare", "Energy", "Capital Goods", "Financial", "Conglomerates", "Services", "Retail"]
max = [float('-inf'), 0]
index = 0
for price in numbers:
    if price > max[0]:
        max[0] = price
        max[1] = index
    index += 1

mycursor = db.cursor()

# insert leading sector info into MySQL table
mycursor.execute("INSERT INTO Sector_Info(name, increase, created) VALUES (%s,%s,%s)", (sectors[max[1]], max[0] , date.today()))

# increase the days_leading count for the leading sector
mycursor.execute("UPDATE Days_Leading SET days_leading = (days_leading + 1) WHERE name = %s", (sectors[max[1]],))
db.commit()

