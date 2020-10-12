import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from selenium import webdriver
import time
from pymongo import MongoClient
import urllib.parse
from bson import json_util
import json

#Connecting to MongoDB
username = urllib.parse.quote_plus('superuser')
password = urllib.parse.quote_plus('p@ss')
client = MongoClient('mongodb://%s:%s@127.0.0.1' % (username, password))


#Creating a database called btcDB and a collection called BTC
btcDB = client['btcDB']
col_btc = btcDB['BTC']


url = "https://www.blockchain.com/btc/unconfirmed-transactions"
options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')
driver = webdriver.Chrome(options=options,executable_path='/usr/bin/chromedriver')
driver.get(url)


def webScraper():
    #Wait 5 seconds before scraping the website so everything loads
    time.sleep(5)

    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')

    l = []

    for link in soup.find_all("div", attrs={"class": "sc-6nt7oh-0 kduRNF"}):
        l.append(link.get_text())

    #Merge every 4 element in the list together so we get hash+time+amount(btc)+amount(usd) as 1 element in the list
    l = iter(l)
    prevs = [c + " " + next(l, ' ') for c in l]
    prevs = iter(prevs)
    prev = [c + " " + next(prevs, ' ') for c in prevs]

    return prev

data = []
while True:
    data = webScraper()

    address = []
    times = []
    amount = []
    price = []

    for i in data:
        transaction = i.split()
        address.append(transaction[0])
        times.append(transaction[1])
        amount.append(transaction[2])
        price.append(transaction[4])
    
    df = pd.DataFrame(list(zip(address,times,amount,price)),columns = ["Hash", "Time", "Amount in BTC", "Amount in USD"])
    df['Amount in BTC'] = df['Amount in BTC'].astype(float)
    df.drop_duplicates(subset=['Hash'])
    print("\n")
    print("Top 10 BTC transactions in the last minute")
    print("\n")
    print(df.sort_values(by=['Amount in BTC'],ascending=False).head(10))

    #df.reset_index(level=0, inplace=True)
    jsonX = (df.sort_values(by=['Amount in BTC'],ascending=False)).head(10).to_json("test.json",orient='records')

    with open('test.json') as f:
        file_data = json.load(f)

    print(file_data)
    x = col_btc.insert_many(file_data)

    #Wait 60 seconds before running the function again
    time.sleep(60)


