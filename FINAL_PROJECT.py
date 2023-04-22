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
    
    conn = sqlite3.connect('EventBrite.db')
    cur = conn.cursor()
    #print(region_list)
    no_dup_list = [*set(region_list)]
    for i in range(len(no_dup_list)):
        cur.execute("INSERT OR IGNORE INTO Regions (id, region) VALUES (?, ?)",(i, no_dup_list[i]))
    #count any column, make into a number in python, 
    #make index what you have for count, when call function, 
    # send with an index, range for loop, index +25 reset when you get to 100



    for i in range(index, index+25):
        cur.execute("INSERT OR IGNORE INTO Names (id, category_id, name, region_id) VALUES (?, ?, ?, ?)",(i, category_list[i], name_list[i], region_id_list[i]))

    conn.commit()


def category_table(url):
    api_url = requests.get(url)
    access_data = api_url.json()
    #print(access_data)
    conn = sqlite3.connect('EventBrite.db')
    cur = conn.cursor()

    #cur.execute("DROP TABLE IF EXISTS Categories")
    #cur.execute("CREATE TABLE IF NOT EXISTS Categories (id INTEGER PRIMARY KEY, name TEXT)")

    id_list = []
    name_list = []
    #for part in access_data:
        #print(part)
    categories = access_data['categories']
    for category in categories:
        #print(category['id'])
        #print(category['name'])
        cur.execute("INSERT OR IGNORE INTO Categories (id, name) VALUES (?,?)", (category['id'], category['name']))
        conn.commit()

'''
This function should also plot two barcharts in one figure. The first bar chart displays the categories 
    along the y-axis and their ratings along the x-axis in descending order (by rating).
    The second bar chart displays the buildings along the y-axis and their ratings along the x-axis 
    in descending order (by rating).
'''
def calculations():
    #print("calm")

    #create separate function for cur and conn?????
    conn = sqlite3.connect('EventBrite.db')
    cur = conn.cursor()

    count_cat_dict = {}
    cat_id_list = [101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 199]
    for x in cat_id_list:
        cur.execute("SELECT COUNT(category_id) FROM Names WHERE category_id = ?", (x,))
    #cur.execute("SELECT COUNT(Categories.name) FROM Names JOIN Categories ON categories.id = Names.category_id")
        count_rough = cur.fetchall()
        count_clean = count_rough[0][0]
        #print(count_clean)
        if count_clean > 0:
            cur.execute("SELECT Categories.name FROM Names JOIN Categories ON Categories.id = Names.category_id WHERE category_id = ?", (x,))
            name_rough = cur.fetchall()
            name_clean = name_rough[0][0]
        #if name_rough != ['']:
        #name_clean = name_rough[0]
            count_cat_dict[name_clean] = count_clean
    #need to write this in a text file
    #print(count_cat_dict)
    return count_cat_dict

def create_visual(dict):
    conn = sqlite3.connect('EventBrite.db')
    cur = conn.cursor()

    names = list(dict.keys())
    values = list(dict.values())

    #plt.barh(names, values, color="pink")
    #plt.title('Types of Popular Events this Month')
    #plt.ylabel('Categories')
    #plt.xlabel('Number of Each')
    #plt.show()
    '''
        cat_dict = {}
    for x in range(1,15):
        cur.execute("SELECT COUNT(category_id) FROM restaurants WHERE category_id = ?", (x,))
        count_rough = cur.fetchall()
        count_clean = count_rough[0][0]
        #print(count_clean)
        cur.execute("SELECT categories.category FROM restaurants JOIN categories ON categories.id = restaurants.category_id WHERE category_id = ?", (x,))
        name_rough = cur.fetchall()
        name_clean = name_rough[0][0]
        #print(name_clean)
        cat_dict[name_clean] = int(count_clean)
    '''
    #test returns a list of tuples, category, Name, region_id

def write_calculations():
    # Write calculations to text file
    f = open("Calculations.txt", "a")
    f.write("EventBrite Calculations\n")
    f.write("\n")
    f.write("Count of EventBrite event types:\n")
    
    string = ""
    for (event, num) in zip(event_types, calculations_lst):
        string = "Percentage of {} events: {}%".format(event, str(num))
        f.write(string)
        f.write("\n")

    # Create pie chart of breakdowns 
    fig, ax = plt.subplots(figsize =(10, 6))
    ax.set_title("SeatGeek Events Breakdown")

'''
def fix_duplicates():
    conn = sqlite3.connect('EventBrite.db')
    cur = conn.cursor()

    cur.execute("SELECT region FROM Names")
    regions = cur.fetchall()
    #print(regions)
    regions_list = []
    remove_dup = [*set(regions)]
    for region in remove_dup:
        region = region[0]
        regions_list.append(region)
    for i in range(len(regions_list)):
        cur.execute("INSERT OR IGNORE INTO Regions (id, region) VALUES (?,?)", (i, regions_list[i]))

    conn.commit()
'''

def join_tables():
    conn = sqlite3.connect('EventBrite.db')
    cur = conn.cursor()
    pass
    #cur.execute("SELECT Names.id,Names.name,Names.region,Categories.name FROM Names JOIN Categories ON Names.category_id = Categories.id")
    #Do the 25 thing here?????




#count any column, make into a number in python, make index what you have for count, when call function, send with an index, range for loop, index +25 reset when you get to 100
#100 rows!!!!

def main():
    if __name__== "__main__" :
        conn = sqlite3.connect('EventBrite.db')
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
        #fix_duplicates()
        #fix_duplicates()
    #if count == 0:
        #get_data()
        cat_count = calculations()
        create_visual(cat_count)
    #cur.execute()

        
        #call_events = make_events_table(index)
        cat_url = category_table('https://www.eventbriteapi.com/v3/categories/?token=F4WRZ3F74TBQCCDAVEQT')
main()