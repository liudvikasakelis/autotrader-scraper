#!/usr/bin/python

# Will take a list of autotrader ad page IDs and scrape useful data from them,
# outputting in .csv format. The scraper function itself can be found in ff1.py

# Takes three arugments, in order: 
# 1. an input file name (one line per ad url)
# 2. an output file name (appends by default)


import sys
import csv
import os

import ff1
    
with open(str(sys.argv[1]), 'r') as i_file: # url file 
    url_list = i_file.readlines()

if os.path.isfile(sys.argv[2]):
    mode = 'a'
else:
    mode = 'w'
    
with open(str(sys.argv[2]), mode) as o_file: 
    i = 0
    field_names = [
        'url', 'status_code', 'make', 'model', 'trim', 'manufactured_year', 
        'condition', 'transmission', 'body_type', 'doors', 
        'engine_size', 'seats', 'fuel_type', 'description', 'price', 
        'townAndDistance', 'isTradeSeller', 'emailAddress', 'tax', 
        'co2Emissions', 'mileage', 'raw_response'
    ]
    cwriter = csv.DictWriter(o_file, fieldnames=field_names)
    
    if mode == 'w':
        cwriter.writeheader()
    for u in url_list:
        tmp = ff1.scraper(u)
        cwriter.writerow(tmp)
        i+=1
        if i % 10 == 0:
            print(i)

print('done')
