# cScrape

A script to check computer gigs or web jobs in each city listed on Craigslist for a specific search term. The script can check every US city automatically or it can be given a specific city or list of cities.

The script primarily uses BeautifulSoup and requests. It also uses PyMongo to store unique gigs in database. 

## Usage

In order to run the script, run the script with argument for either auto search or manual search, e.g
python scraper.py -t manual will run the script for targeted search. It will ask for search term, e.g "developer" and 
city as well, e.g "new york city". Running the script with the auto flag will ask for search term and then go through each city listed 
on Craigslist.
