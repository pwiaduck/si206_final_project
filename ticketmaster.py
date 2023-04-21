import requests
import json
import sqlite3
import matplotlib.pyplot as plt

# Connect to the database
conn = sqlite3.connect('final.db')
cursor = conn.cursor()

# Create the tables for genre and ticketmaster if they don't exist
cursor.execute('''CREATE TABLE IF NOT EXISTS genretable
               (genre_id INTEGER PRIMARY KEY,
                Genre TEXT)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS ticketmaster
               (event_id TEXT PRIMARY KEY,
                genre INTEGER,
                price INTEGER,
                FOREIGN KEY (genre) REFERENCES genretable(genre_id))''')

# Set the API parameters
api_key = "fcNg8br5TNEGoumOPyL7jGL2QbgJZILz"
url = "https://app.ticketmaster.com/discovery/v2/events"
params = {
   "apikey": api_key,
   "size": 25
}

# Retrieve events in batches of 25 and store them in the database
for i in range(0, 100, 25):
   params["page"] = i // 25
   response = requests.get(url, params=params)
   data = json.loads(response.text)
   ticketmaster = data["_embedded"]["events"]

   # Insert the data into the ticketmaster table
   # Insert the data into the ticketmaster table
for event in ticketmaster:
   genre = event["classifications"][0]["genre"]["name"]
   price = event["priceRanges"][0]["min"] if "priceRanges" in event else None
   
   # Check if the event_id already exists in the ticketmaster table
   cursor.execute('''SELECT event_id FROM ticketmaster WHERE event_id = ?''', (event["id"],))
   existing_event_id = cursor.fetchone()

   # If the event_id doesn't exist, insert the data into the ticketmaster table
   if existing_event_id is None:
      # Check if the genre already exists in the genretable
      cursor.execute('''SELECT genre_id FROM genretable WHERE Genre = ?''', (genre,))
      genre_id = cursor.fetchone()

      # If the genre doesn't exist, insert it into the genretable with a unique ID
      if genre_id is None:
         cursor.execute('''INSERT INTO genretable (Genre) VALUES (?)''', (genre,))
         genre_id = cursor.lastrowid
      else:
         genre_id = genre_id[0]

      # Insert the data into the ticketmaster table
      cursor.execute('''INSERT OR IGNORE INTO ticketmaster (event_id, genre, price)
                  VALUES (?, ?, ?)''', (event["id"], genre_id, price))



# Commit the changes to the database
conn.commit()

# Join the genretable datatable and the ticketmaster datatable to update the genre to use unique IDs
cursor.execute('''SELECT t.event_id, g.genre_id, t.price 
                  FROM ticketmaster t JOIN genretable g ON t.genre = g.genre_id''')
rows = cursor.fetchall()

# Update the ticketmaster table with the unique genre IDs and designated price
cursor.execute('''DROP TABLE IF EXISTS ticketmaster''')
cursor.execute('''CREATE TABLE ticketmaster (
                     event_id TEXT PRIMARY KEY,
                     genre INTEGER,
                     price INTEGER,
                     FOREIGN KEY (genre) REFERENCES genretable(genre_id))''')
cursor.executemany('''INSERT INTO ticketmaster (event_id, genre, price)
                      VALUES (?, ?, ?)''', rows)

# Commit the changes and close the connection to the database
conn.commit()

# Join the genretable datatable and the ticketmaster datatable to retrieve genre names
cursor.execute('''SELECT g.Genre, t.price 
                  FROM ticketmaster t JOIN genretable g ON t.genre = g.genre_id''')
rows = cursor.fetchall()

# Convert the data to a dictionary
genre_prices = {}
for tup in rows:
    genre = tup[0]
    price = tup[1]

    if price is not None:
        price = float(price)

        if genre in genre_prices:
            genre_prices[genre].append(price)
        else:
            genre_prices[genre] = [price]

# Calculate the average prices for each genre
avg_prices = {}
for genre, prices in genre_prices.items():
    avg_price = sum(prices) / len(prices)
    avg_prices[genre] = avg_price


# Write calculations to text file
    f = open("Calculations.txt", "w")
    f.write("TicketMaster Calculations\n")
    f.write("\n")
    f.write("Average TicketMaster Ticket Prices by Event Genre/Type\n")
    
    for genre, price in avg_prices.items():
        calculationwrite = f.write(f"Average price of {genre}: {price}\n")

# Get the keys and values for plotting
genre = list(avg_prices.keys())
avgprices = list(avg_prices.values())

# Set the figure size
plt.figure(figsize=(6, 4))

# Define a list of colors
colors = ['red', 'orange', 'yellow', 'green', 'blue', 'purple', 'pink', 'indigo', 'brown']

# Plot the bar graph with the specified colors
plt.bar(range(len(avg_prices)), avgprices, tick_label=genre, color=colors)

# Add y-axis label
plt.ylabel('Average Price')

# Add x-axis label
plt.xlabel('Event Genre/Type')

# Set the title of the graph
plt.title('Average Ticket Prices by Event Genre/Type')

# rotate x-axis labels by 30 degrees
plt.xticks(rotation=30)

# Adjust the bottom margin to make the x-axis label visible
plt.subplots_adjust(bottom=0.2)

plt.show()


conn.close()