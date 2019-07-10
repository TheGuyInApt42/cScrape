from bs4 import BeautifulSoup
import requests
from fake_useragent import UserAgent
import time
import random
import datetime
from pymongo import MongoClient

ua = UserAgent()
client = MongoClient()
db = client.cScrape
gigs = db.Gigs


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

def get_result_rows(info, city):
    if info:
        for r in info:
            print('Wait time in second loop is {} seconds'.format(wait_time))
            time.sleep(wait_time) #wait 30 - 60 secs in between
            post_time = r.find('time').attrs['datetime']
            title = r.find('a').text
            post_id = r.find('a').attrs['data-id']
            print(post_id, post_time, title, city)

            gig = {
                "c_id": post_id,
                "post_title": title,
                "city": city,
                "post_date": post_time,
                "insert_date": datetime.datetime.utcnow()
            }

            old_gig = gigs.find_one({'c_id': post_id})
            if old_gig:
                print('Already seen.')
            else:
                gig_id = gigs.insert_one(gig).inserted_id
            
            
        print('Returned {} results'.format(len(info)))
    else:
        print('No results.')

#TODO: think about adding search params i.e search titles only
def doSearch(cities_list, wait_time, search_query, search_type='auto'):
    if search_type == 'manual':
        location = input('Enter city to check: ')
        city_index = get_specific_city(cities_list, location)
        city_link = cities_list[city_index].find('a')
        current_city = cities_list[city_index].text
        print('Checking {}'.format(current_city)) # show what city is being checked
        gigs_url =  '{}{}'.format(city_link['href'], gigs_param)
        complete_url = '{}{}'.format(gigs_url, search_query)
        info = process_url(complete_url, 'p', 'result-info')
        get_result_rows(info, current_city)
    
    elif search_type == 'auto':
        for i in range(0,len(cities_list)):
            print('Wait time in first loop for city {} is {} secs'.format(i, wait_time))
            time.sleep(wait_time) #wait between 30 - 1 minutes before each
            
            city_link = cities_list[i].find('a')
            current_city = cities_list[i].text
            print('Checking {}'.format(current_city))# show what city is being checked
            gigs_url =  '{}{}'.format(city_link['href'], gigs_param)
            complete_url = '{}{}'.format(gigs_url, search_query)
            info = process_url(complete_url, 'p', 'result-info')
            get_result_rows(info, current_city)
            wait_time = random.randint(30, 60) 
    




''' Start script '''
data = process_url(start_endpoint, 'div', 'colmask')
cities = get_cities(data)


search_term = input('Enter search term: ')
search_query = '?query={}&is_paid=all'.format(search_term)

doSearch(cities, wait_time, search_query)

# TODO: add progress bar/counter