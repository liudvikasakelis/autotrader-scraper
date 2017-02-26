# autotrader-scraper
Autotrader.co.uk data scraper. 

Do I get a slap on the wrist or how does this work?

While the project is mostly functional, it's poorly documented, which is what I'm focusing on at the moment.

# Structure

* ff1.py    The main library, containing the scraper function + other things
* scraper.py    Kind of a wraper for the scraper function
* listmaker.py  Makes list of car IDs
* srv.py  The (incomplete) server that should automate all the scraping. Documentation to follow 

all will be explained!

### What I want from you, reader

* Triangulation. Here's my idea: we query the same car page from 3 different postcodes, get the distances, then triangulate. Help me out here!


