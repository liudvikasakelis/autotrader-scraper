#!/usr/bin/python

# Will take a list of autotrader ad page IDs and scrape useful data from them,
# outputting in .csv format. The scraper function itself can be found in ff1.py

# Takes three arugments, in order: 
# 1. an input file name (containing a pickled list of ad IDs)
# 2. an output file name 
# 3. an optional "a" to append to an existing output file
# !!WILL OVERWRITE OTHERWISE, SO CAREFUL!!

import sys

import pickle
import csv

import ff1
    
with open(str(sys.argv[1]), 'rb') as i_file: # our ID file
    url_list = pickle.load(i_file) 

if len(sys.argv) > 3: # append mode available by adding "a" after output file
    if sys.argv[3] == "a": 
        mode = 'ab'
else:
    mode = 'wb'

with open(str(sys.argv[2]), mode) as o_file: 
    cwriter = csv.writer(o_file)
    i = 0
    toprow = ['url', 'make', 'model', 'engine_size', 'year', 'body_type', 
              'mileage','transmission', 'fuel', 'co2_emissions', 'doors', 
              'seats', 'category', 'engine_power', 'drive_train', 'price', 
              'seller', 'full_desc', 'last_seen', 'first_gone']
    if mode == 'wb':
        cwriter.writerow(toprow)
    for u in url_list:
        cwriter.writerow(ff1.scraper(u))
        i+=1
        if i % 10 == 0:
            print i

print 'done'
