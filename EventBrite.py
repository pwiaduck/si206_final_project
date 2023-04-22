from bs4 import BeautifulSoup
import requests
import os
import csv
import sqlite3
import unittest
import json
import re
import matplotlib.pyplot as plt

def make_events_table(index):

    event_id_list = []
    url_list = []
    ending_list = ['', '?page=2', '?page=3', '?page=4', '?page=5']
    for ending in ending_list:
        url = f"https://www.eventbrite.com/d/online/all-events/{ending}"
        url_list.append(url)

    for url in url_list:
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')

        tester = soup.find_all('script', type='text/javascript')
        for lines in tester:
            text = lines.text
            text_string = re.findall('eid=[0-9]+', text)
            for event_id in text_string:
                stripped = event_id.strip('eid=')
                event_id_list.append(stripped)

    name_list = []
    region_list = []
    category_list = []

    for event_id in event_id_list:
        api_url = f"https://www.eventbriteapi.com/v3/events/{event_id}/?token=F4WRZ3F74TBQCCDAVEQT"
        api_url_req = requests.get(api_url)
        access_data = api_url_req.json()
    
        start_time = access_data['start']
        region = start_time.get('timezone')
        region_list.append(region)
    

        names = access_data['name'].get('text')
        name_list.append(names)

        category_id = access_data['category_id']
        category_list.append(category_id)

        #could also do a month variable

    region_id_list = []
    for region in region_list:
        if region == 'America/Costa_Rica':
            region_id = 4
        if region == 'America/Denver':
            region_id = 10
        if region == 'America/Chicago':
            region_id = 8
        if region == 'America/Vancouver':
            region_id = 0
        if region == 'Africa/Nairobi':
            region_id = 11
        if region == 'America/Toronto':
            region_id = 9
        if region == 'Europe/London':
            region_id = 7
        if region == 'Europe/Berlin':
            region_id = 1
        if region == 'Europe/Dublin':
            region_id = 3
        if region == 'America/New_York':
            region_id = 6
        if region == 'America/Los_Angeles':
            region_id = 2
        if region == 'Australia/Sydney':
            region_id = 5
        region_id_list.append(region_id)

    conn = sqlite3.connect('final.db')
    cur = conn.cursor()

    no_dup_list = [*set(region_list)]
    for i in range(len(no_dup_list)):
        cur.execute("INSERT OR IGNORE INTO Regions (id, region) VALUES (?, ?)",(i, no_dup_list[i]))

    for i in range(index, index+25):
        cur.execute("INSERT OR IGNORE INTO Names (id, category_id, name, region_id) VALUES (?, ?, ?, ?)",(i, category_list[i], name_list[i], region_id_list[i]))

    conn.commit()


def category_table(url):
    api_url = requests.get(url)
    access_data = api_url.json()
    #print(access_data)
    conn = sqlite3.connect('final.db')
    cur = conn.cursor()


    id_list = []
    name_list = []

    categories = access_data['categories']
    for category in categories:

        cur.execute("INSERT OR IGNORE INTO Categories (id, name) VALUES (?,?)", (category['id'], category['name']))
    conn.commit()

def calculations():

    conn = sqlite3.connect('final.db')
    cur = conn.cursor()

    count_cat_dict = {}
    cat_id_list = [101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 199]
    for x in cat_id_list:
        cur.execute("SELECT COUNT(category_id) FROM Names WHERE category_id = ?", (x,))
        count_rough = cur.fetchall()
        count_clean = count_rough[0][0]

        if count_clean > 0:
            cur.execute("SELECT Categories.name FROM Names JOIN Categories ON Categories.id = Names.category_id WHERE category_id = ?", (x,))
            name_rough = cur.fetchall()
            name_clean = name_rough[0][0]

            count_cat_dict[name_clean] = count_clean

    return count_cat_dict

def extra_calculations():
    conn = sqlite3.connect('final.db')
    cur = conn.cursor()

    count_reg_dict = {}
    for x in range(0,11):
        cur.execute("SELECT COUNT(region_id) FROM Names WHERE region_id = ?", (x,))

        count_rough = cur.fetchall()
        count_clean = count_rough[0][0]

        if count_clean > 0:
            cur.execute("SELECT Regions.region FROM Names JOIN Regions ON Regions.id = Names.region_id WHERE region_id = ?", (x,))
            name_rough = cur.fetchall()
   
            name_clean = name_rough[0][0]
 
            count_reg_dict[name_clean] = count_clean

    return count_reg_dict

def extra_visualization(dict):
    conn = sqlite3.connect('final.db')
    cur = conn.cursor()

    names = list(dict.keys())
    values = list(dict.values())

    plt.barh(names, values, color="magenta")
    plt.title('Events per Region this Month')
    plt.ylabel('Region')
    plt.xlabel('Number of Events')
    plt.show()

def write_calculations(dict):
    # Write calculations to text file
    f = open("Calculations.txt", "a")
    f.write("EventBrite Calculations\n")
    f.write("\n")
    f.write("Count of Popular EventBrite event types:\n")
    
    names = list(dict.keys())
    values = list(dict.values())

    string = ""
    for (key, val) in zip(names, values):
        string = f"{key}: {val} events"

        f.write(string)
        f.write("\n")


def create_visual(dict):
    conn = sqlite3.connect('final.db')
    cur = conn.cursor()

    names = list(dict.keys())
    values = list(dict.values())

    plt.barh(names, values, color="pink")
    plt.title('Types of Popular Events this Month')
    plt.ylabel('Categories')
    plt.xlabel('Number of Each')
    plt.show()



def main():
    if __name__== "__main__" :
        conn = sqlite3.connect('final.db')
        cur = conn.cursor()
        #cur.execute("DROP TABLE IF EXISTS Names")
        cur.execute("CREATE TABLE IF NOT EXISTS Names (id INTEGER PRIMARY KEY, category_id INTEGER, name TEXT, region_id INTEGER)")
        cur.execute("CREATE TABLE IF NOT EXISTS Categories (id INTEGER PRIMARY KEY, name TEXT)")
        cur.execute("CREATE TABLE IF NOT EXISTS Regions (id INTEGER PRIMARY KEY, region TEXT)")

        cur.execute("SELECT COUNT('id') FROM Names")
        count = cur.fetchall()
        count = (count[0])
        count = count[0]

        index = count
        #index = 0

        if count <= 100:
            cur.execute("CREATE TABLE IF NOT EXISTS Names (id INTEGER PRIMARY KEY, category_id INTEGER, name TEXT, region TEXT)")
            index = 0
            if count == 25:
                index = 25
            elif count == 50:
                index = 50
            elif count == 75:
                index = 75
            else:
                index = 0
        
        #print(count)
        #print(index)
        make_events_table(index)

        cat_url = category_table('https://www.eventbriteapi.com/v3/categories/?token=F4WRZ3F74TBQCCDAVEQT')
        cat_count = calculations()
        reg_count = extra_calculations()
        extra_visualization(reg_count)
        write_calculations(cat_count)
        create_visual(cat_count)
    #cur.execute()

        
        #call_events = make_events_table(index)
        #cat_url = category_table('https://www.eventbriteapi.com/v3/categories/?token=F4WRZ3F74TBQCCDAVEQT')
main()