from bs4 import BeautifulSoup
import requests
from fake_useragent import UserAgent

ua = UserAgent()

header = {'User-Agent':str(ua.firefox)}

start_endpoint = 'https://www.craigslist.org/about/sites'

result = requests.get(start_endpoint, headers=header)
content = result.content

soup = BeautifulSoup(content, features='html.parser')
divs = soup.find_all('div', {'class': 'colmask'})
us_locations =divs[0]
cities = us_locations.find_all('li')


# print cities[10]
# city_link = cities[10].find('a')
# print city_link['href']


gigs_param = 'd/computer-gigs/search/cpg'

query = raw_input('Enter search term: ')
search_query = '?query={}&is_paid=all'.format(query)


for i in range(0,len(cities)):
    city_link = cities[i].find('a')
    gigs_url =  '{}{}'.format(city_link['href'], gigs_param)
    complete_url = '{}{}'.format(gigs_url, search_query)

    res = requests.get(complete_url, headers=header)
    data = res.content
    newsoup = BeautifulSoup(data, features='html.parser')

    results = newsoup.find_all('a', {'class': 'result-title'})
    result

    if results:
        for r in results:
            print r.text, r.attrs['data-id']
