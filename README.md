# autotrader-scraper
Autotrader.co.uk data scraper.

Exports to a sqlite3 database and keeps it really tidy.

Just moved to python3, so bugs should be expected. More documentation on the way

# Structure

* ff1.py    The main library, containing the scraper function + other things
* scraper.py    Kind of a wraper for the scraper function DEPRECATED
* listmaker.py  Makes list of car IDs DEPRECATED 
* srv.py  The main server. Run the file with python3, communicate with using client.py. 
* client.py Client library. Import to python3, run client.add_query(postcode, radius, min_price, max_price) to add jobs to server job queue and watch them appear in the database. Shutdown server with client.shutdown()


