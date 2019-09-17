# Listmaker
# Usage:
# ./listmaker.py https://www.autotrader.co.uk/car-search?advert... url_list.txt 
# if file exists, we append

import sys
import csv
import os

import ff1

base_url = sys.argv[1]
out_fname = sys.argv[2]

if not os.path.isfile(out_fname):
    z = file.open(out_fname, 'w')
    z.close()
    
page_count = 1 
while True:
    results = ff1.search_result_scraper(base_url + '&page=' + str(page_count))
    if len(results) > 0:
        with open(out_fname, 'a') as fcon:
            for r in results:
                fcon.write('https://www.autotrader.co.uk' + r)
                fcon.write('\n')
        page_count += 1
        print(len(results))
    else:
        break
