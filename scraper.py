from bs4 import BeautifulSoup
import requests


url = 'https://www.craigslist.org/about/sites'

result = requests.get(url)
content = result.content

soup = BeautifulSoup(content, features='html.parser')
divs = soup.find_all('div', {'class': 'colmask'})
us_locations =divs[0]
cities = us_locations.find_all('li')

print cities[0]
city_link = cities[0].find('a')
print city_link['href']

gigs_url = 'd/computer-gigs/search/cpg'
print '{}{}'.format(city_link['href'], gigs_url)