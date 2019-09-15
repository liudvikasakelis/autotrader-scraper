# autotrader-scraper
Autotrader.co.uk data scraper.

I'm revisiting this ancient project because I saw 8 people starred it, and I 
felt very guilty for not providing them with at least an honest attempt.

A lot 
has changed since it last worked: I believe autotrader has changed their site 
layout at least 2 times, and also Trump is now president. The former doesn't 
make for a simple scrape. They somehow transitioned to behemoth javascript 
systems running in the front end, making requests for data after the main html
has loaded. This is tricky, because when scraping, we don't usually want to run 
all this javascript all just to make a single request for the data. 

Luckily, most modern browsers let you monitor outgoing HTTP requests (browsers 
are making those requests after all, there's no way to hide it). It's rather 
trivial to find the request that returns a nice JSON with all the basic car 
information. The request url is then simple to modify to make a request for 
any ad we like. See the ff1.py file, scraper function to see how simple it has
become - very little regex and absolutely no xpath. 

This is not always the case, so we did get extremely lucky with autotrader 
building their site this way. It may very well change some time in the future. 

# Structure

* `ff1.py`   The main library, containing a number of scraper functions. 
Be sure to handle the possible exceptions if you choose to use them. 

* `scraper.py`  Scrapes a list of ad urls into a csv file, lacking only a 
listmaker (to make said list).

* `listmaker.py`  Makes list of car IDs by query - not done yet, but coming 
very very soon.

* `srv.py`  **DEPRECATED**, because it's a very hardcore way to do what I think should 
be casual scraping. It didn't solve the problem it was meant to (time away 
requests so the site doesn't get wise to us scraping). Turns out, their pretty 
much only criterion for IP bans is hits per units of time, not any patterns.
The only real way to get around this is a proxy list, which flies right out of 
the territory of casual scraping. Feel free to implement one yourself if you 
need the ads so badly. 

* client.py **DEPRECATED** really, a simple listmaker ought to be enough for 
everyone™

