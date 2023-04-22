import requests
import json
import sqlite3
import matplotlib.pyplot as plt


# Connect to the database
conn = sqlite3.connect('final.db')
cursor = conn.cursor()


def make_tables(index):
   # Set the API parameters
   api_key = "fcNg8br5TNEGoumOPyL7jGL2QbgJZILz"
   url = "https://app.ticketmaster.com/discovery/v2/events"
   params = {
       "apikey": api_key,
       "size": 100
   }


   # Create empty lists for event ids, genres, and prices
   event_ids = []
   genres = []
   prices = []


   # Retrieve events and append the data to the lists
   response = requests.get(url, params=params)
   data = json.loads(response.text)
   ticketmaster = data["_embedded"]["events"]


   for event in ticketmaster:
       eventid = event["id"]
       genre = event["classifications"][0]["genre"]["name"]
       price = event["priceRanges"][0]["min"] if "priceRanges" in event else None


       # Append the data to the respective lists
       event_ids.append(event["id"])
       genres.append(genre)
       prices.append(price)
#    print(event_ids)
#    print(genres)
#    print(prices)
   lst = []
   for genre in genres:
       if genre == 'R&B':
           genre_id = 1
       if genre == 'Rock':
           genre_id = 2
       if genre == 'Basketball':
           genre_id = 3
       if genre == 'Country':
           genre_id = 4
       if genre == 'Hockey':
           genre_id = 5
       if genre == 'Pop':
           genre_id = 6
       if genre == 'Soccer':
           genre_id = 7
       if genre == 'Baseball':
           genre_id = 8
       if genre == 'Motorsports/Racing':
           genre_id = 9 
       

       
       lst.append(genre_id)
    #    print(lst)

   for i in range(index, index+25):
       cursor.execute("INSERT OR IGNORE INTO ticketmaster (event_id, genre, price) VALUES (?, ?, ?)", (event_ids[i], lst[i], prices[i]))


       # Check if the genre already exists in the genretable
       cursor.execute('''SELECT genre_id FROM genretable WHERE Genre = ?''', (genres[i],))
       genre_id = cursor.fetchone()


       # If the genre doesn't exist, insert it into the genretable with a unique ID
       if genre_id is None:
           cursor.execute('''INSERT INTO genretable (Genre) VALUES (?)''', (genres[i],))
           genre_id = cursor.lastrowid
       else:
           genre_id = genre_id[0]


       # Insert the data into the ticketmaster table
       cursor.execute('''INSERT OR IGNORE INTO ticketmaster (event_id, genre, price) VALUES (?, ?, ?)''', (event_ids[i], genre_id, prices[i]))

   conn.commit()


def main():
   cursor.execute('''CREATE TABLE IF NOT EXISTS genretable (genre_id INTEGER PRIMARY KEY, Genre TEXT)''')
   cursor.execute('''CREATE TABLE IF NOT EXISTS ticketmaster (event_id TEXT PRIMARY KEY, genre INTEGER, price INTEGER, FOREIGN KEY (genre) REFERENCES genretable(genre_id))''')
   cursor.execute("SELECT COUNT('price') FROM ticketmaster")
   count = cursor.fetchall()
   count = count[0]
   count = count[0]

   index = count

   if count <= 100:
       cursor.execute('''CREATE TABLE IF NOT EXISTS ticketmaster (event_id TEXT PRIMARY KEY, genre INTEGER, price INTEGER, FOREIGN KEY (genre) REFERENCES genretable(genre_id))''')
       index = 0
       if count == 25:
           index = 25
       elif count == 50:
           index = 50
       elif count == 75:
           index = 75
       else:
           index = 0
   make_tables(index)


main()

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

print(avg_prices)


# Write calculations to text file
f = open("Calculations.txt", "a")
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

