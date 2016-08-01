from selenium import webdriver
import json
from time import *
import datetime
import sys

with open('cookies.json') as data_file:    
    cookies = json.load(data_file)

all_photos = set()
    
def scrollToBottom(driver):
    attempts = 0
    lastheight = 0

    els = [0]
    
    while len(els) != 5:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sleep(0.1)
        els = driver.find_elements_by_xpath("//div[@data-sigil='m-loading-indicator-animate m-loading-indicator-root'][@class='_2so _2sq _2ss img _50cg']")
        sys.stdout.write('.')
        sys.stdout.flush()

        height = driver.execute_script("return(document.body.scrollHeight);")
        
        if (height == lastheight):
            attempts += 1
        else:
            attempts = 0

        if attempts > 40:
            break
    
    print('.')

def getUserIds(driver):
    driver.get('https://m.facebook.com/williams.logan/friends/');
    
    scrollToBottom(driver)
    
    user_ids = set()
    
    user_elements = driver.find_elements_by_css_selector('._52jh a')
    
    for user_element in user_elements:
        user_link = user_element.get_attribute('href')
        if user_link is not None:
            user = user_link[23:].split('/')[0]
            if (user is not 'settings') and (user is not 'findfriends'):
                user_ids.add(user)
    
    return list(user_ids)

def getPhotoIds(driver):
    links = driver.find_elements_by_tag_name('a')
    photo_ids = set()

    for link in links:
        if link.get_attribute('href') is not None:
            if 'facebook.com/photo.php' in link.get_attribute('href'):
                fbid = link.get_attribute('href').split('fbid=')
                if len(fbid) > 1:
                    photo_ids.add(fbid[1].split('&')[0])
    
    return photo_ids

driver = webdriver.PhantomJS()
driver.get('https://m.facebook.com/williams.logan/friends/')

for cookie in cookies:
    driver.add_cookie(cookie)

user_ids = getUserIds(driver)
driver.quit()
print(len(user_ids))

prevlen = 0

f = open('all_photos_2012.txt', 'w')

for year in ['2012', '2011', '2010']:
    driver = webdriver.PhantomJS()

    for cookie in cookies:
        driver.add_cookie(cookie)
        
    for user_id in user_ids[24:]:
        

        print("Load page for user '" + user_id + "', year " + year)
        driver.get('https://m.facebook.com/' + user_id + '/year/' + year + '/')
        scrollToBottom(driver)

        photos = getPhotoIds(driver)
        all_photos.update(photos)

        print("    " + str(len(photos)) + " photos added to " + str(len(all_photos)) + " so far")
        
        if (len(photos) == prevlen):
            driver.quit()
            
            driver = webdriver.PhantomJS()

            for cookie in cookies:
                driver.add_cookie(cookie)
                
            print("Reloading page for user '" + user_id + "', year " + year)
            driver.get('https://m.facebook.com/' + user_id + '/year/' + year + '/')
            scrollToBottom(driver)

            photos = getPhotoIds(driver)
            all_photos.update(photos)

            print("    " + str(len(photos)) + " photos added to " + str(len(all_photos)) + " so far")
        
        prevlen = len(photos)

        for photoid in photos:
            f.write(photoid + '\n')

    
    driver.quit()

f.close()
