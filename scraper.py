from bs4 import BeautifulSoup
import requests
from fake_useragent import UserAgent
import time
import random

ua = UserAgent()


wait_time = random.randint(30, 120) 
# print 'header is {} and initial wait time is {} secs'.format(ua.random, wait_time)

start_endpoint = 'https://www.craigslist.org/about/sites'
gigs_param = 'd/computer-gigs/search/cpg'


def process_url(url, tag, className):
    header = {'User-Agent':str(ua.random)} # get random header string
    result = requests.get(url, headers=header)
    content = result.content

    soup = BeautifulSoup(content, features='html.parser')
    return soup.find_all(tag, {'class': className})
    


def get_cities(processed_data):
    us_locations = processed_data[0]
    return us_locations.find_all('li')

#TODO: work on this more
def check_city(cities_list, city='new york'):
    for idx, elem in enumerate(cities_list):
        pass
        #if city in elem.text:
         #   print idx, elem.text
    # print cities[10]
    # city_link = cities[10].find('ya')
    # print city_link['href']
    


data = process_url(start_endpoint, 'div', 'colmask')
cities = get_cities(data)

location = raw_input('Enter city to check: ')
check_city(cities)

if location == 'durham':
    print 'yes'



#query = raw_input('Enter search term: ')
#search_query = '?query={}&is_paid=all'.format(query)

'''

for i in range(0,len(cities)):
    time.sleep(wait_time) #wait between 30 - 2 minutes before each
    print 'Wait time in first loop for city {} is {} secs'.format(i, wait_time)
    
    city_link = cities[i].find('a')
    current_city = cities[i].text
    print 'Checking {}'.format(current_city) # show what city is being checked
    gigs_url =  '{}{}'.format(city_link['href'], gigs_param)
    complete_url = '{}{}'.format(gigs_url, search_query)

    info = process_url(complete_url, 'p', 'result-info')

    if info:
        for r in info:
            time.sleep(wait_time) #wait between 30 - 2 minutes before each again
            print 'Wait time in second loop is {} seconds'.format(wait_time)
            post_time = r.find('time').attrs['datetime']
            title = r.find('a').text
            post_id = r.find('a').attrs['data-id']
            print post_id, post_time, title, current_city
            wait_time = random.randint(30, 120) 
'''