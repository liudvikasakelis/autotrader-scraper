#!/usr/bin/python
import sys, re, requests, csv
from lxml import html
import math, time, pickle

postcode = sys.argv[1]
radius = sys.argv[2]
minprice = sys.argv[3] 
maxprice = sys.argv[4]
if len(sys.argv) < 6:
    outputfile = (sys.argv[1] + "-" + sys.argv[2] + "-" 
                  + sys.argv[3] + "-" + sys.argv[4] + '.txt')
else:
    outputfile = sys.argv[5]
pageno = 1 

url = ("http://www.autotrader.co.uk/car-search?radius=" + str(radius) 
       + "&postcode=" + str(postcode) 
       + "&price-from" + str(minprice) 
       + "&price-to=" + str(maxprice) 
       + "&page=" )

ad_ids = [] 

page = requests.get(url+str(pageno)) 
time.sleep(1)     
t = html.fromstring(page.content) 
v = t.xpath('//div[@class="search-result__r1"]/div/a/@href') 
t_cars = t.xpath('//h1[@class="search-form__count js-results-count"]/text()')[0]
t_cars = re.search('[0-9,]+', t_cars).group(0)
t_cars = int(t_cars.replace(",", ""))
print("A total of " + str(t_cars) 
      + " cars in " + str(t_cars/10) + " page(s)")

if t_cars > 1000:
    print("Only the first 1000 cars can be retrieved from autotrader.co.uk")
    t_cars = 1000
ad_ids = [None]*t_cars
totalpgs = int(math.ceil(float(t_cars)/10))
i = 0
for pageno in range(1, totalpgs+1):
    print pageno
    page = requests.get(url+str(pageno)) 
    t = html.fromstring(page.content)
    v = t.xpath('//div[@class="search-result__r1"]/div/a/@href')
    for a in v:
        ad_ids[i] = int(re.search('(?<=classified/advert/)[0-9]+', a).group(0))
        i+=1

with open(str(outputfile), "wb") as fl:
    pickle.dump(ad_ids, fl)

