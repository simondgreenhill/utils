'''
Scrape GAEZ data from https://webarchive.iiasa.ac.at/Research/LUC/GAEZv3.0/
'''

__author__ = 'Simon Greenhill'
__contact__ = 'sgreenhill@uchicago.edu'

import os
import time
import itertools
import warnings
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from urllib.request import urlretrieve

options = Options()
options.set_headless(headless=False)

def waitwrapper(driver, p, time=10):
    '''
    wrapper for WebDriverWait
    '''
    WebDriverWait(driver, time).until(lambda x:
        len(x.find_elements_by_xpath(p)) > 0)

def login(url='http://www.gaez.iiasa.ac.at/w/ctrl?_flow=Vwr&_view=Type&idAS=0&idFS=0&fieldmain=main_py_yld_agcl&idPS=bc885d41888f234be1c086131cbbfe95c19c8499&dimType=il'):
    '''
    Initiate a Chrome driver and log into GAEZ website
    '''
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    driver.find_element_by_name('_username').send_keys() # username here
    driver.find_element_by_name('_password').send_keys() # password here
    driver.find_element_by_id('buttonSubmit__login').click()
    return driver

def navigate_to_agro_climatic_yield(driver):
    # navigate to the agro-climatic yield values
    driver.find_element_by_xpath('/html/body/div[1]/div/form/div[4]/div[1]/div/fieldset/ul/li[1]/input').click()
    # click on agro-climatically attainable yield
    driver.find_element_by_xpath('/html/body/div[1]/div/form/div[4]/div[1]/div[1]/fieldset/ul/li[1]/div/ul/li[1]/input').click()
    return driver


def logout(driver):
    driver.find_element_by_xpath('/html/body/div[1]/div/form/div[3]/div[2]/div[1]/input').click()
    driver.close()


def select_crop(driver, crop):
    # wait until ready
    p = '/html/body/div[1]/div/form/div[3]/div[1]/div/fieldset[2]/ul/li[1]/input'
    waitwrapper(driver, p)
    
    # navigate to crop selection
    driver.find_element_by_xpath(p).click()
    # navigate to 'cereals'
    if crop in ['wheat', 'wetland_rice', 'dryland_rice', 'maize', 'sorghum']:
        type_path = '/html/body/div[1]/div/form/div[4]/div[1]/fieldset/input[1]'
        # navigate to crop-specific values
        if crop == 'wheat':
            i = 2
        elif crop == 'wetland_rice':
            i = 3
        elif crop == 'dryland_rice':
            i = 4
        elif crop == 'maize':
            i = 5
        elif crop == 'sorghum':
            i = 7
        else:
            raise NotImplementedError('Not implemented for {}'.format(crop))
        
        c = '/html/body/div[1]/div/form/div[4]/div[1]/fieldset/input[{}]'.format(i)
    
    elif crop in ['cassava']:
        type_path = '/html/body/div[1]/div/form/div[4]/div[1]/fieldset/input[2]'
        c = '/html/body/div[1]/div/form/div[4]/div[1]/fieldset/input[5]'
        
    elif crop in ['cotton']:
        type_path = '/html/body/div[1]/div/form/div[4]/div[1]/fieldset/input[8]'
        c = '/html/body/div[1]/div/form/div[4]/div[1]/fieldset/input[9]'

    elif crop in ['soy']:
        type_path = '/html/body/div[1]/div/form/div[4]/div[1]/fieldset/input[5]'
        c = '/html/body/div[1]/div/form/div[4]/div[1]/fieldset/input[6]' 
    else:
        raise NotImplementedError('Not implemented for {}'.format(crop))

    # navigate to "type" menu (cereal, tuber, etc.)
    driver.find_element_by_xpath(type_path).click()
    # select crop
    driver.find_element_by_xpath(c).click()

    return driver


# select water supply
def select_water(driver, water):
    # wait until browser is ready
    p = '/html/body/div[1]/div/form/div[3]/div[1]/div/fieldset[2]/ul/li[2]/input'
    waitwrapper(driver, p)

    # navigate to water supply selection
    driver.find_element_by_xpath(p).click()
    if water == 'rainfed':
        i = 1   
    else:
        i = 2
    driver.find_element_by_xpath('/html/body/div[1]/div/form/div[4]/div[1]/fieldset/input[{}]'.format(i)).click()
    
    return driver


def select_input(driver, input):
    # wait until ready
    p = '/html/body/div[1]/div/form/div[3]/div[1]/div/fieldset[2]/ul/li[3]/input'
    waitwrapper(driver, p)
    
    # navigate to input level
    driver.find_element_by_xpath(p).click()
    if input == 'high':
        i = 1
    elif input == 'intermediate':
        i = 2
    elif input == 'low':
        i = 3

    driver.find_element_by_xpath('/html/body/div[1]/div/form/div[4]/div[1]/fieldset/input[{}]'.format(i)).click()
    return driver


def select_time_period(driver):
    # Select time period. We only want the "baseline" values, so no options here
    # wait until ready
    p = '/html/body/div[1]/div/form/div[3]/div[1]/div/fieldset[2]/ul/li[4]/input'
    waitwrapper(driver, p)

    # navigate to time period
    driver.find_element_by_xpath(p).click()
    driver.find_element_by_xpath('/html/body/div[1]/div/form/div[4]/div[1]/fieldset[2]/input').click()
    
    return driver


def save(driver, default_path, new_path, name, crop, water, input):
    '''
    Save the map that was produced.
    '''
    # navigate to map
    p1 = '/html/body/div[1]/div/form/div[3]/div[1]/div/fieldset[4]/ul/li[1]/input'
    waitwrapper(driver=driver, p=p1, time=30)
    driver.find_element_by_xpath(p1).click()
    try:
        # click on zip file icon
        driver.find_element_by_xpath('/html/body/div[1]/div/form/div[4]/div[1]/div[3]/div[3]/a[4]/img').click()
        # wait until download is done
        time.sleep(15)

    # some input-water combinations seem to not be possible. if this is the case,
    # give a warning and move on
    except NoSuchElementException:
        warnings.warn('{} {} {} failed'.format(crop, water, input))
        return driver

    # find the most recently edited file in the directory
    file =  max([f for f in os.scandir(default_path)], key=lambda x: x.stat().st_mtime).name

    # rename the file to the desired name
    os.makedirs(new_path, exist_ok=True)
    os.rename('{}/{}'.format(default_path, file), '{}/{}.zip'.format(new_path, name))

    return driver

def download_gaez(crop, water, input, 
                  savepath='/Users/simongreenhill/Downloads/'):
    ''' 
    Put together all the steps above to download the data
    '''
    print('Downloading {} {} {}'.format(crop, water, input))
    
    driver = login()
    driver = navigate_to_agro_climatic_yield(driver)
    driver = select_crop(driver, crop)
    driver = select_water(driver, water)
    driver = select_input(driver, input)
    driver = select_time_period(driver)
    new_path = '{}/GAEZ/{}/{}/'.format(savepath, input, water)
    driver = save(driver, savepath, new_path, crop, crop, water, input)
    logout(driver)

# download gaez for all crops, irrigation, input levels
crops = ['cassava', 'cotton', 'maize', 'dryland_rice', 'wetland_rice',
         'sorghum', 'soy', 'wheat']
irrigations = ['irrigated', 'rainfed']
input_levels = ['high', 'intermediate', 'low']

args = pd.DataFrame(list(itertools.product(crops, irrigations, input_levels)))

[download_gaez(crop, water, input) for crop, water, input 
 in zip(args[0], args[1], args[2])]


def set_bounds(clip_bounds, y_train, y_test):
    if None in clip_bounds:
        print("")
        print("Setting clip bounds to min/max")
        # Replace none with min or max
        for ix, i in enumerate(clip_bounds)        
            # Assert that it has two values
            assert len(i) == 2

            if i[0]==None:
                i[0] = np.min(np.append(y_train, y_test))
            if i[1]==None:
                i[1] = np.max(np.append(y_train, y_test))
            
        print(clip_bounds)

    return clip_bounds


# map(download_gaez, args[0], args[1], args[2])
