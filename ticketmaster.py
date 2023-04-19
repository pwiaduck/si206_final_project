import sqlite3
import requests
import json
import matplotlib.pyplot as plt

# connect to the database
conn = sqlite3.connect('mydatabase.db')
cursor = conn.cursor()

# create the events table if it doesn't exist
cursor.execute('''CREATE TABLE IF NOT EXISTS ticketmaster
                (id TEXT PRIMARY KEY,
                 name TEXT,
                 venue_name TEXT,
                 price_range TEXT,
                 genre TEXT)''')

# set the API parameters
api_key = "fcNg8br5TNEGoumOPyL7jGL2QbgJZILz"
url = "https://app.ticketmaster.com/discovery/v2/events"
params = {
    "apikey": api_key,
    "size": 25
}

# retrieve events in batches of 25 and store them in the database
for i in range(0, 100, 25):


    params["page"] = i // 25

    response = requests.get(url, params=params)
    data = json.loads(response.text)

    ticketmaster = data["_embedded"]["events"]
    for event in ticketmaster:
        # Check if the "dateTime" key exists in the "start" dictionary
        if "dateTime" in event["dates"]["start"]:
            start_time = event["dates"]["start"]["dateTime"]
        else:
            start_time = None
        
        data = (event["id"],
                event["name"],
                event["_embedded"]["venues"][0]["name"],
                event["priceRanges"][0]["min"] if "priceRanges" in event else None,
                event["classifications"][0]["genre"]["name"] if "classifications" in event and "genre" in event["classifications"][0] else None)
        
        cursor.execute('INSERT OR IGNORE INTO ticketmaster VALUES (?, ?, ?, ?, ?)', data)
        
        conn.commit()

cursor.execute('SELECT genre, price_range FROM ticketmaster')
data = cursor.fetchall()

genre_prices = {}
for row in data:
    genre = row[0]
    price = row[1]

    if price is not None:
        price = float(price)

        if genre in genre_prices:
            genre_prices[genre].append(price)
        else:
            genre_prices[genre] = [price]

avg_prices = {}
for genre, prices in genre_prices.items():
    avg_price = sum(prices) / len(prices)
    avg_prices[genre] = avg_price

# convert to json
json_data = json.dumps(avg_prices)

# load the JSON data back to a dictionary
avg_prices_dict = json.loads(json_data)
print(avg_prices_dict)

# get the keys and values for plotting
genre = list(avg_prices_dict.keys())
avgprices = list(avg_prices_dict.values())

# plot the bar graph
plt.bar(range(len(avg_prices_dict)), avgprices, tick_label=genre)
plt.show()

conn.close()