# functions
import re


def fipa(q, param): # matches param to list entries, returns entry after match
    for a in range(len(q)):
        if q[a] == param :
            return q[a+1]


def lpat(q, pattern): # sees if list element matches regex, returns element
    for a in q:
        if re.match(pattern, a):
            return a


def scraper(urlid):
    import re, requests
    from lxml import html
    import time

    fuelTypes = ['Petrol', 'Diesel', 'Hybrid', 'Electric', 'Bi Fuel']
    bodyTypes = ['MPV', 'Convertible', 'SUV', 'Estate', 'Coupe', 'Saloon', 
                                                             'Hatchback']
    trnsTypes = ['Manual', 'Automatic', 'Semi-Automatic']
    nl = [None]*20
    
    nl[0] = urlid 
    
    aurl = 'http://www.autotrader.co.uk/classified/advert/'
    params = ''
    
    try:
        page = requests.get(aurl+str(urlid)+params) 
    except:
        nl[1] = "AUTOTRADER_FAILED"
        return nl
    
    if(str(page)=='<Response [204]>'):
        nl[1] = "AUTOTRADER_FAILED"
        return nl

    tree = html.fromstring(page.content)
     
    if not re.search('Practicality', page.content): # ad gone 
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

    if re.search('(?<=category=)\w', cat):
        cat = re.search('(?<=category=)\w', cat).group(0)
    else:
        cat = None
   
    nl[1] = re.search('(?<=make=).*(?=&)', v).group(0) # make
    nl[2] = re.search('(?<=model=).*', v).group(0) # model

    try:
        nl[3] = lpat(p, '[0-9]+.[0-9]+L')[:-1] # engine size in L
    except TypeError:    
        nl[3] = -1

    try: 
        nl[4] = int(lpat(p, '[0-9]{4}')) # year
    except TypeError:
        nl[4] = -1

    try:
        nl[5] = list(set(bodyTypes).intersection(p))[0] # body type
    except IndexError:
        nl[5] = -1

    try:
        nl[6] = lpat(p, '[0-9]+,[0-9]+ miles')[:-6] # mileage in a string
        nl[6] = int(nl[6].replace(",", ""))
    except TypeError:
        nl[6] = -1

    try:
        nl[7] = list(set(trnsTypes).intersection(p))[0] # transmission
    except IndexError:
        nl[7] = -1

    try:
        nl[8] = list(set(fuelTypes).intersection(p))[0] # fuel type
    except IndexError:
        nl[8] = -1

    try:
        nl[9] = int(fipa(q, " emissions")[:-4]) # co2 emissions
    except ValueError:
        nl[9] = -1

    try:
        nl[10] = int(fipa(q, "No. of doors")) # doors 
    except ValueError:
        nl[10] = -1
    
    try:
        nl[11] = int(fipa(q, "No. of seats")) # seats 
    except ValueError:
        nl[11] = -1

    nl[12] = cat # category
    
    try:
        nl[13] = int(fipa(q, "Engine power")[:-4]) # engine power, in bhp
    except ValueError:
        nl[13] = -1
    
    nl[14] = fipa(q, "Drivetrain") # drivetrain
    nl[15] = re.search('(?<=vehicle_price":")[0-9]*', z).group(0) # price 
    nl[16] = re.search('(?<=type":")\w+', z).group(0) # 
    # nl[18] = re.search('(?<=postcode":")\w+', z).group(0) # postcode
    nl[17] = desc
    nl[18] = int(time.time())
    
    return nl





