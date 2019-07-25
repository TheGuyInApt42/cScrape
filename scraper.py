'''
This script allows searching of Craigslist computer gigs either manually searching a specific city 
or automatically searching every city listed in the US.

'''
import argparse
from bs4 import BeautifulSoup
import requests
from fake_useragent import UserAgent
import time
import random
import datetime
from pymongo import MongoClient

ap = argparse.ArgumentParser()
ap.add_argument("-t", "--target", help="flag for searching either gigs or web jobs")
# add argument var for running manual script
ap.add_argument("-s", "--style", help="flag to run single, multiple, or all cities search")
args = vars(ap.parse_args())
print("Running {} script on {}".format(args["style"], args["target"]))


ua = UserAgent() #instantiate user agent object for setting user agent strings

# connect to database
client = MongoClient()
db = client.cScrape
gigs = db.Gigs


wait_time = random.randint(30, 60) #set wait time for random time between 30 - 60 secs

start_endpoint = 'https://www.craigslist.org/about/sites' # Craigslist locations url
gigs_param = 'd/computer-gigs/search/cpg' # url parameter that gets appended for computer gigs 
web_jobs_param = 'd/web-html-info-design/search/web' # url parameter that gets appended for web jobs


def process_url(url, tag, className):
    ''' 
    Processes url and returns a list of a specific tag with certain class, i.e list of all 'divs' with class name 'container'
    Takes a url, HTML tag, class name of tag searching for
    Returns list of bs4 elements that fit the desired criteria
    '''
    header = {'User-Agent':str(ua.random)} # get random header string
    # print('Header for this request is {}'.format(header))
    result = requests.get(url, headers=header) #load url with random header string
    content = result.content

    soup = BeautifulSoup(content, features='html.parser')
    return soup.find_all(tag, {'class': className})
    

def get_cities(processed_data):
    '''
    Gets all US cities links Returns list of line tags of all US cities
    Takes in processed data which is a list produced from process_url function
    Returns list of bs4 line elements
    TODO: can maybe extend to other countries
    '''
    us_locations = processed_data[0] # gets first div in list which is the US
    return us_locations.find_all('li')


def get_city_index(cities_list, city='new york'):
    '''
    Gets index number of a specific city in the list of cities
    Takes in a list containing the cities and a city to search for (Default is NYC)
    Returns index number
    '''
    for idx, elem in enumerate(cities_list):
        if city in elem.text:
            return idx

def get_result_rows(results, city, search_type='all'):
    '''
    Checks if there are results and if so, then loops through each result while waiting a random time in between
    Inserts row info into database if it is not already in db
    Takes in list of rows, current city being processed and whether search type is single, multiple or all
    '''
    wait_time = 5 # wait 5 secs between each iteration (should be on same page so dont have to fire anymore new requests)
    if results:
        print('Found {} results'.format(len(results))) # print number of results
        print('Current wait time between results is {} seconds'.format(wait_time))
        for result in results:
            time.sleep(wait_time) 
            post_time = result.find('time').attrs['datetime']
            title = result.find('a').text
            post_id = result.find('a').attrs['data-id']
            link = result.find('a')['href']
            if search_type == 'single':
                print('Position: {}    Date Posted: {}    Link: {}'.format(title, post_time, link))
            # FIXME: add case for multi city search
            elif search_type == 'all':
                #gig object to insert into database
                gig = {
                    "c_id": post_id,
                    "post_title": title,
                    "city": city,
                    "post_date": post_time,
                    "insert_date": datetime.datetime.utcnow()
                }

                old_gig = gigs.find_one({'c_id': post_id}) # check if gig is already in database
                if old_gig:
                    print('This gig is already in database')
                else:
                    gig_id = gigs.insert_one(gig).inserted_id # insert into database if not in it already
                    print('Gig {} has been inserted into database'.format(gig_id))
            
        
    else:
        print('No results found.')

def process_city():
    pass

#TODO: think about adding search params i.e search titles only
def doSearch(cities_list, wait_time, search_term, search_target, search_type='all'):
    '''
    Performs either targeted search or automatic search of all cities
    Takes in list of cities, initial wait time, term to search for, and whether search is single, multiple, or all
    '''
    if search_type == 'single':
        location = input('Enter city to check: ')
        city_index = get_city_index(cities_list, location)
        if city_index: #if city is on craigslist
            city_link = cities_list[city_index].find('a')
            current_city = cities_list[city_index].text
            print('Checking {}'.format(current_city)) # show what city is being checked

            if search_target == 'gigs':
                url =  '{}{}'.format(city_link['href'], gigs_param) # append computer gig parameter to city link
                search_query = '?query={}&is_paid=all'.format(search_term)
            else: 
                url = '{}{}'.format(city_link['href'], web_jobs_param)
                search_query = '?query={}'.format(search_term)
            complete_url = '{}{}'.format(url, search_query)
            info = process_url(complete_url, 'p', 'result-info')
            get_result_rows(info, current_city,'single')
        
        else: 
            print('Sorry, city not found on Craigslist')
    
    elif search_type == 'all':
        for i in range(0,len(cities_list)):
            print('Current wait time for next result is {} secs'.format(wait_time))
            time.sleep(wait_time) #wait between 30 - 1 minutes before each
            
            city_link = cities_list[i].find('a')
            current_city = cities_list[i].text
            print('Checking {}'.format(current_city))# show what city is being checked
            if search_target == 'gigs':
                url =  '{}{}'.format(city_link['href'], gigs_param) # append computer gig parameter to city link
                search_query = '?query={}&is_paid=all'.format(search_term)
            else: 
                url = '{}{}'.format(city_link['href'], web_jobs_param)
                search_query = '?query={}'.format(search_term)
            complete_url = '{}{}'.format(url, search_query)
            info = process_url(complete_url, 'p', 'result-info')
            get_result_rows(info, current_city)
            wait_time = random.randint(30, 60) 
    
    else:
        locations = list(map(str, input('Enter cities to check: ').split(', ')))
        print(locations)
        for city in locations:
            city_index = get_city_index(cities_list, city)
            if city_index: #if city is on craigslist
                city_link = cities_list[city_index].find('a')
                current_city = cities_list[city_index].text
                print('Checking {}'.format(current_city)) # show what city is being checked

                if search_target == 'gigs':
                    url =  '{}{}'.format(city_link['href'], gigs_param) # append computer gig parameter to city link
                    search_query = '?query={}&is_paid=all'.format(search_term)
                else: 
                    url = '{}{}'.format(city_link['href'], web_jobs_param)
                    search_query = '?query={}'.format(search_term)
                complete_url = '{}{}'.format(url, search_query)
                info = process_url(complete_url, 'p', 'result-info')
                get_result_rows(info, current_city,'single')
            
            else: 
                print('Sorry, city not found on Craigslist')
    



''' Start script '''
data = process_url(start_endpoint, 'div', 'colmask')
cities = get_cities(data)


search_term = input('Enter search term: ')
doSearch(cities, wait_time, search_term, args["target"], args["style"])

# TODO: add progress bar/counter
# TODO: thinking about multiple search terms i.e ['developer', 'freelance']
