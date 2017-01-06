#!/usr/bin/python
import ff1, csv, sys, pickle
    
with open(str(sys.argv[1]), 'rb') as cfile: # file with a list of IDs
    url_list = pickle.load(cfile) 

if len(sys.argv) > 3:
    if sys.argv[3] == "a":
        mode = 'ab'
else:
    mode = 'wb'

with open(str(sys.argv[2]), mode) as o_file: # output to this
    cwriter = csv.writer(o_file)
    i = 0
    toprow = ['url', 'make', 'model', 'engine_size', 'year', 'body_type', 
            'mileage','transmission', 'fuel', 'co2_emissions', 'doors', 
            'seats', 'category', 'engine_power', 'drive_train', 'price', 
            'seller', 'full_desc', 'last_seen', 'first_gone']
    if mode == 'wb':
        cwriter.writerow(toprow)
    for u in url_list:
        cwriter.writerow(ff1.scrapper(u))
        i+=1
        if i % 10 == 0:
            print i

print 'done'
