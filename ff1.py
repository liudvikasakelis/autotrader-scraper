#!/usr/bin/python3

import re
import requests
from lxml import html
import time
import math
import json


def scraper(url):
    urlid = re.findall('[0-9]{11,}', url)[0]
    base_url = 'https://www.autotrader.co.uk/json/fpa/initial/'
    response = requests.get(base_url + str(urlid), timeout=5)
    
    ret = dict()
    
    ret['url'] = url
    ret['status_code'] = response.status_code
    if response.status_code != 200:
        return ret
    
    ret['raw_response'] = response.content.decode('utf-8')
    
    d = json.loads(response.content.decode('utf-8'))
    
    keys_vehicle = {
        'make', 'model', 'trim', 'condition', 'tax', 'co2Emissions'
    }
    for nm in set(d['vehicle'].keys()).intersection(keys_vehicle):
        ret[nm] = d['vehicle'][nm]
        
    keys_keyFacts = {
        'engine-size', 'manufactured-year', 'body-type', 'mileage', 
        'transmission', 'fuel-type', 'doors', 'seats'
    }
    for nm in set(d['vehicle']['keyFacts'].keys()).intersection(keys_keyFacts):
        ret[nm] = d['vehicle']['keyFacts'][nm]
        
    if 'doors' in ret.keys():
        match = re.search('\d+', ret['doors'])
        if match:
            ret['doors'] = match[0]
    
    if 'seats' in ret.keys():
        match = re.search('\d+', ret['seats'])
        if match:
            ret['seats'] = match[0]
    
    if 'manufactured-year' in ret.keys():
        match = re.search('\d{4}', ret['manufactured-year'])
        if match:
            ret['manufactured-year'] = match[0]
            
    if 'mileage' in ret.keys():
        ret['mileage'] = re.sub('[^\d\.]', '', ret['mileage'])
    
    if 'co2Emissions' in ret.keys():
        ret['co2Emissions'] = re.sub('[^\d\.]', '', ret['co2Emissions'])
    
    
    keys_advert = {'price', 'description'}
    for nm in set(d['advert'].keys()).intersection(keys_advert):
        ret[nm] = d['advert'][nm]
        
    if 'price' in ret.keys():
        ret['price'] = re.sub('[^\d]', '', ret['price'])
    
    keys_seller = {'isTradeSeller', 'townAndDistance', 'emailAddress'}
    for nm in set(d['seller'].keys()).intersection(keys_seller):
        ret[nm] = d['seller'][nm]
        
    keys_tracking = {
        'average_mpg', 'vehicle_check_status'
    }
    for nm in set(d['pageData']['tracking'].keys()).intersection(keys_seller):
        ret[nm] = d['pageData']['tracking'][nm]
        
    for nm in ret.keys():
        ret[re.sub('-', '_', nm)] = ret.pop(nm)
                   
    return ret


def tree_getter(url):
    try:
        page = requests.get(url)
    except requests.exceptions.RequestException:
        return -2
    if page.status_code == 204:
        return -1
    # print(page.content[:200])
    return html.fromstring(page.content)


def search_result_scraper(url):
    response = requests.get(url, timeout=5)
    tree = html.fromstring(response.content.decode('utf-8'))
    res = set(tree.xpath('//a[contains(@class, "listing-fpa-link")]/@href'))
    return(list(res))
    
    

def c_scraper(url):
    tree = tree_getter(url)
    if isinstance(tree, int):
        return tree
    try:
        print()
        car_count = int(
            re.sub(
                '[^0-9]', 
                '', 
                tree.xpath('//h1[@class="search-form__count js-results-count"]/text()')[0]
            )
        )
        page_count = int(math.ceil(car_count / 10))
        print(page_count)
    except IndexError:
        print('IndexError')
        return 0
    return page_count
