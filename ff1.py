#!/usr/bin/python3
# works, but could use some cleanup (scraper function esp)

import re
import requests
from lxml import html
import time


def fipa(q, param):
    """matches param to list entries, returns next entry after match"""
    for a in range(len(q)):
        if q[a] == param:
            return q[a + 1]


def lpat(q, pattern):
    """sees if list element matches regex, returns element"""
    for a in q:
        if re.match(pattern, a):
            return a


# FIXME: This method is way too long.
def scraper(urlid):
    fuelTypes = ['Petrol', 'Diesel', 'Hybrid', 'Electric', 'Bi Fuel']
    bodyTypes = ['MPV', 'Convertible', 'SUV', 'Estate', 'Coupe', 'Saloon',
                 'Hatchback']
    trnsTypes = ['Manual', 'Automatic', 'Semi-Automatic']
    nl = [None] * 20

    nl[0] = urlid

    aurl = 'http://www.autotrader.co.uk/classified/advert/'
    params = ''

    try:
        page = requests.get(aurl + str(urlid) + params)
    except Exception:
        # FIXME: No exception defined
        nl[1] = "AUTOTRADER_FAILED"
        return nl

    if page.status_code == 204:
        nl[1] = "AUTOTRADER_FAILED"
        return nl

    tree = html.fromstring(page.content)

    if not re.search('Practicality', page.content.decode('UTF-8')):  # ad gone
        nl[19] = int(time.time())  # first_gone field
        return nl

    # ???
    v = tree.xpath('//link[@rel="canonical"]/@href')[0]
    # kfacts
    p = tree.xpath('//ul[@class="fpaGallery__sidebar__keyFacts"]/li/text()')
    # specs
    q = tree.xpath('//div[@class="fpaSpecifications__listItem"]/div/text()')
    # utag_data
    z = tree.xpath('//script[contains(.,"vehicle_price")]/text()')
    # full desc
    desc = tree.xpath('//section[@class="fpaDescription"]/text()')[0]
    # just the good bits
    z = re.search('(?<=utag_data = {).*(?=})', z[0]).group(0)
    cat = tree.xpath('//a[@class="tracking-motoring-products-link"]/@href')[0]

    # TODO: Is it everything fine with backslash(\) in strings?
    if re.search('(?<=category=)\w', cat):
        cat = re.search('(?<=category=)\w', cat).group(0)
    else:
        cat = '0'

    if re.search('(?<=make=).*(?=&)', v):
        nl[1] = re.search('(?<=make=).*(?=&)', v).group(0)  # make

    if re.search('(?<=model=).*', v):
        nl[2] = re.search('(?<=model=).*', v).group(0)  # model

    try:
        nl[3] = lpat(p, '[0-9]+.[0-9]+L')[:-1]  # engine size in L
    except TypeError:
        nl[3] = -1

    try:
        nl[4] = int(lpat(p, '[0-9]{4}'))  # year
    except TypeError:
        nl[4] = -1

    try:
        nl[5] = list(set(bodyTypes).intersection(p))[0]  # body type
    except IndexError:
        nl[5] = -1

    try:
        nl[6] = lpat(p, '[0-9]+,[0-9]+ miles')[:-6]  # mileage in a string
        nl[6] = int(nl[6].replace(",", ""))
    except TypeError:
        nl[6] = -1

    try:
        nl[7] = list(set(trnsTypes).intersection(p))[0]  # transmission
    except IndexError:
        nl[7] = -1

    try:
        nl[8] = list(set(fuelTypes).intersection(p))[0]  # fuel type
    except IndexError:
        nl[8] = -1

    try:
        nl[9] = int(fipa(q, " emissions")[:-4])  # co2 emissions
    except ValueError:
        nl[9] = -1

    try:
        nl[10] = int(fipa(q, "No. of doors"))  # doors
    except ValueError:
        nl[10] = -1

    try:
        nl[11] = int(fipa(q, "No. of seats"))  # seats
    except ValueError:
        nl[11] = -1

    nl[12] = cat  # category

    try:
        nl[13] = int(fipa(q, "Engine power")[:-4])  # engine power, in bhp
    except ValueError:
        nl[13] = -1

    nl[14] = fipa(q, "Drivetrain")  # drivetrain
    nl[15] = re.search('(?<=vehicle_price":")[0-9]*', z).group(0)  # price
    nl[16] = re.search('(?<=type":")\w+', z).group(0)
    # nl[18] = re.search('(?<=postcode":")\w+', z).group(0) # postcode
    nl[17] = desc
    nl[18] = int(time.time())

    return nl


def tree_getter(url):
    try:
        page = requests.get(url)
    except requests.exceptions.RequestException:
        return -2
    if page.status_code == 204:
        return -1
    return html.fromstring(page.content)


def b_scraper(url):
    tree = tree_getter(url)
    if isinstance(tree, int):
        return tree
    rtn = []
    id_strings = tree.xpath('//li[@class="search-page__result"]/@id')
    for element in id_strings:
        try:
            ele_int = int(element)
            rtn.append(ele_int)
        except ValueError:
            pass
    return rtn


def c_scraper(url):
    tree = tree_getter(url)
    if isinstance(tree, int):
        return tree
    try:
        page_number = int(tree.xpath('//li[@class="paginationMini__count"]/strong[2]/text()')[0])
    except IndexError:
        return 0
    return page_number
