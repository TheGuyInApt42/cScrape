# cScrape

A script to check computer gigs in each city listed on Craigslist either automatically or manually selecting a city.

The script primarily uses BeautifulSoup and requests. It also uses PyMongo to store unique gigs in database. 

# Usage

In order to run the script, run the script with argument for either auto search or manual search, e.g
python scraper.py -t manual will run the script for targeted search. It will ask for search term, e.g "developer" and 
city as well, e.g "new york city". Running the script with the auto flag will ask for search term and then go through each city listed 
on Craigslist.
