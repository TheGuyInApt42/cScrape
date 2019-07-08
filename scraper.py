from bs4 import BeautifulSoup
import requests
from fake_useragent import UserAgent
import time
import random

ua = UserAgent()

header = {'User-Agent':str(ua.random)} # get random header string

wait_time = random.randint(30, 120) 
print 'header is {} and initial wait time is {} secs'.format(ua.random, wait_time)

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

#TODO: add functionality for checking specific city

gigs_param = 'd/computer-gigs/search/cpg'

query = raw_input('Enter search term: ')
search_query = '?query={}&is_paid=all'.format(query)


for i in range(0,len(cities)):
    time.sleep(wait_time) #wait between 30 - 2 minutes before each
    print 'Wait time in first loop for city {} is {} secs'.format(i, wait_time)
    
    city_link = cities[i].find('a')
    current_city = cities[i].text
    print 'Checking {}'.format(current_city) # show what city is being checked
    gigs_url =  '{}{}'.format(city_link['href'], gigs_param)
    complete_url = '{}{}'.format(gigs_url, search_query)

    res = requests.get(complete_url, headers=header)
    data = res.content
    newsoup = BeautifulSoup(data, features='html.parser')

    results = newsoup.find_all('p', {'class': 'result-info'})

    if results:
        for r in results:
            time.sleep(wait_time) #wait between 30 - 2 minutes before each again
            print 'Wait time in second loop is {} seconds'.format(wait_time)
            post_time = r.find('time').attrs['datetime']
            title = r.find('a').text
            post_id = r.find('a').attrs['data-id']
            print post_id, post_time, title, current_city
            wait_time = random.randint(30, 120) 
