'''
Creator: Ralph Gorham

This script allows searching of Craigslist computer gigs either manually searching a specific city 
or automatically searching every city listed in the US.

Updated 7/27/19

'''
import argparse
from bs4 import BeautifulSoup
import requests
from fake_useragent import UserAgent
import time
import random
import datetime
from pymongo import MongoClient
import smtplib, ssl
import settings

from lxml import html
import requests

ap = argparse.ArgumentParser()
ap.add_argument("-t", "--target", help="flag for searching either gigs or web jobs")
# add argument var for running manual script
ap.add_argument("-s", "--style", help="flag to run single, multiple, or all cities search")
ap.add_argument("-a", "--auto", help="flag to check whether to run auto or manual")
args = vars(ap.parse_args())
print("Running {} script on {}".format(args["style"], args["target"]))


ua = UserAgent() #instantiate user agent object for setting user agent strings

# connect to database
client = MongoClient()
db = client.cScrape
gigs = db.Gigs


SLEEPTIME = random.randint(3600, 5400) #set sleep time for random time between 60 - 90 minutes

start_endpoint = 'https://www.craigslist.org/about/sites' # Craigslist locations url
gigs_param = 'd/computer-gigs/search/cpg' # url parameter that gets appended for computer gigs 
web_jobs_param = 'd/web-html-info-design/search/web' # url parameter that gets appended for web jobs
software_jobs_param = 'd/software-qa-dba-etc/search/sof' # url parameter for software jobs


def process_url(url, objectToFind):
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

    if objectToFind['identifier'] == 'class':
        data = soup.find_all(objectToFind['tag'], {'class': objectToFind['className']})
    else:
        data = soup.find(objectToFind['tag'], id=objectToFind['id_'])
    return data
    

def xpath(url='https://newyork.craigslist.org/brk/cpg/d/brooklyn-user-testers-for-an-apparel/6942975936.html'):
    pageContent=requests.get(url)
    tree = html.fromstring(pageContent.content)
    test = tree.xpath('//*[@id="postingbody"]/a')
    print(test)

    return test


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


def process_city(target, city, link, term, searchtype):
    print('Checking {}'.format(city))# show what city is being checked
    if target == 'gigs':
        url =  '{}{}'.format(link['href'], gigs_param) # append computer gig parameter to city link
        search_query = '?query={}&is_paid=all'.format(term)
    elif target == 'web': 
        url = '{}{}'.format(link['href'], web_jobs_param)
        search_query = '?query={}'.format(term)
    else:
        url = '{}{}'.format(link['href'], software_jobs_param)
        search_query = '?query={}'.format(term)
    complete_url = '{}{}'.format(url, search_query)

    #FIXME: change name of obj var
    obj = { "identifier": "class", "tag": "p", "className": "result-info"}

    info = process_url(complete_url, obj)
    newPosts = get_result_rows(info, city, searchtype)
    #TODO: add software job search

    return newPosts


def get_result_rows(results, city, search_type='specific'):
    '''
    Checks if there are results and if so, then loops through each result while waiting a random time in between
    Inserts row info into database if it is not already in db
    Takes in list of rows, current city being processed and whether search type is specific or all
    '''
    newPosts = []
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

            obj = { "identifier": "element", "tag": "section", "id_": "postingbody"}

            #FIXME: work on this
            #p_info = process_url(link, obj) # get post information

            #t = xpath(link)
            
                
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
                newPosts.append('Position: {}    Date Posted: {}    Link: {}'.format(title, post_time, link))

            if search_type == 'specific':
                print('Position: {}    Date Posted: {}    Link: {}'.format(title, post_time, link))
                #print(p_info[2:4])
                

        
    else:
        print('No results found.')

    return newPosts

'''
def postInfo(post_link):
    result = requests.get(post_link) #load url with random header string
    content = result.content

    soup = BeautifulSoup(content, features='html.parser')
    data = soup.find('section', id='postingbody')
    return data.text
'''

#TODO: think about adding search params i.e search titles only
def doSearch(cities_list, search_term, locations, search_target, search_type='specific'):
    '''
    Performs either targeted search or automatic search of all cities
    Takes in list of cities, initial wait time, term to search for, and whether search is specific or all
    '''
    wait_time = random.randint(30, 60)
    if search_type == 'specific':
        for city in locations:
            city_index = get_city_index(cities_list, city)
            if city_index: #if city is on craigslist
                city_link = cities_list[city_index].find('a')
                current_city = cities_list[city_index].text
                newPosts = process_city(search_target, current_city, city_link, search_term, search_type)
            
            else: 
                print('Sorry, city not found on Craigslist')
    
    elif search_type == 'all':
        #TODO: maybe add functionality to exclude specific cities
        for i in range(0,len(cities_list)):
            print('Current wait time for next result is {} secs'.format(wait_time))
            time.sleep(wait_time) #wait between 30 - 1 minutes before each
            
            city_link = cities_list[i].find('a')
            current_city = cities_list[i].text
            process_city(search_target, current_city, city_link, search_term, search_type)
            
            wait_time = random.randint(30, 60)
    return newPosts



def emailer(newPosts):
    smtp_server = "smtp.gmail.com"
    port = 587  # For starttls
    
    messsage = ''
    emailTo = 'ralphjgorham@gmail.com'
    message = 'Subject: Craigslist Positions \n\n {}'.format(messsage)
    for post in newPosts:
        message = message+post+"\n\n"

    # Create a secure SSL context
    context = ssl.create_default_context()

    try:
        server = smtplib.SMTP(smtp_server, port)
        server.starttls(context=context)  
        server.login(settings.EMAIL, settings.PASSWORD)
        server.sendmail(settings.EMAIL, emailTo, message)
    except Exception as e:
        print(e)
    finally:
        server.quit()


''' Start script '''
if args["auto"] == 'manual':
    obj = { "identifier": "class", "tag": "div", "className": "colmask"}

    data = process_url(start_endpoint, obj)
    cities = get_cities(data)


    search_term = input('Enter search term: ')
    locations = list(map(str, input('Enter cities to check: ').split(', ')))
    posts = doSearch(cities, search_term, locations, args["target"], args["style"])

    if posts:
        emailer(posts)
        print('Emailing you new results')

else:
    print('Hello friend, I am cScrape!')
    print('I will check Craigslist for new job postings every {:2.0f} minutes'.format(SLEEPTIME/60))
    search_term = input('Enter search term: ')
    locations = list(map(str, input('Enter cities to check: ').split(', '))) #TODO: maybe add this as arg var as well as term(s)
    while args["auto"] == 'auto':
        obj = { "identifier": "class", "tag": "div", "className": "colmask"}

        data = process_url(start_endpoint, obj)
        cities = get_cities(data)

        posts = doSearch(cities, search_term, locations, args["target"], args["style"])

        if posts:
            emailer(posts)
            print('Emailing you new results')
        time.sleep(SLEEPTIME)



# TODO: thinking about multiple search terms i.e ['developer', 'freelance']
