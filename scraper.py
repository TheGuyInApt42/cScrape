from bs4 import BeautifulSoup
import requests
from fake_useragent import UserAgent
import time
import random

ua = UserAgent()

wait_time = random.randint(30, 60) 
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


def get_specific_city(cities_list, city='new york'):
    for idx, elem in enumerate(cities_list):
        if city in elem.text:
            return idx


def doSearch(cities_list, wait_time, search_query, search_type='auto'):
    if search_type == 'manual':
        location = input('Enter city to check: ')
        city_index = get_specific_city(cities_list, location)
        city_link = cities_list[city_index].find('a')
        current_city = cities_list[city_index].text
        print('Checking {}'.format(current_city)) # show what city is being checked
        gigs_url =  '{}{}'.format(city_link['href'], gigs_param)
    
    elif search_type == 'auto':
        for i in range(0,len(cities_list)):
            time.sleep(wait_time) #wait between 30 - 1 minutes before each
            #print 'Wait time in first loop for city {} is {} secs'.format(i, wait_time)
            
            city_link = cities_list[i].find('a')
            current_city = cities_list[i].text
            print('Checking {}'.format(current_city))# show what city is being checked
            gigs_url =  '{}{}'.format(city_link['href'], gigs_param)
            
    complete_url = '{}{}'.format(gigs_url, search_query)
    print(complete_url)

    info = process_url(complete_url, 'p', 'result-info')
    

    if info:
        for r in info:
            time.sleep(20) #wait 20 secs in between
            print('Wait time in second loop is {} seconds'.format(wait_time))
            post_time = r.find('time').attrs['datetime']
            title = r.find('a').text
            post_id = r.find('a').attrs['data-id']
            print(post_id, post_time, title, current_city)
        print('Returned {} results'.format(len(info)))




''' Start script '''
data = process_url(start_endpoint, 'div', 'colmask')
cities = get_cities(data)


search_term = input('Enter search term: ')
search_query = '?query={}&is_paid=all'.format(search_term)

doSearch(cities, wait_time, search_query)

# TODO: add progress bar/counter