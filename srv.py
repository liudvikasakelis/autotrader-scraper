#!/usr/bin/python3
""" going to add separate work lists"""

import socket
import threading
import socketserver
import time
import random
import pickle
import requests
import re
from lxml import html
import ff1
import sqlite3


def sql_writer():
    global STAHP
    global rlist
    with sqlite3.connect('test.db') as conn:
        c = conn.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS cars ('
                  'url INTEGER PRIMARY KEY,'
                  ' make TEXT,'
                  ' model TEXT,'
                  ' engine_size NUM,'
                  ' year INT,'
                  ' body_type TEXT,'
                  ' mileage NUM,'
                  ' transmission TEXT,'
                  ' fuel TEXT,'
                  ' co2_emissions NUM,'
                  ' doors INT,'
                  ' seats INT,'
                  ' category TEXT,'
                  ' engine_power NUM,'
                  ' drive_train TEXT,'
                  ' price NUM,'
                  ' seller TEXT,'
                  ' full_desc TEXT,'
                  ' last_seen NUM,'
                  ' first_gone NUM);')

        while not STAHP:
            while(rlist):
                job = rlist[0]
                c.execute("SELECT * FROM cars WHERE url=?", [job[0]])
                match = list(c.fetchall())
                if(match):
                    final = combine_lines(match, job)
                else:
                    final = job
                c.execute("DELETE FROM cars WHERE url=?", [job[0]])
                c.execute(
                    'INSERT INTO cars VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?'
                    ',?,?,?,?,?,?)', final)
                rlist.remove(job)
            conn.commit()
            time.sleep(5)


# def do_job(job):


def do_a(job):
    result = ff1.scraper(job[1])

    if result[1] == 'AUTOTRADER_FAILED':
        print("Server failed")
        time.sleep(60)
        return 1

    rlist.append(result)
    print("A")
    return 0


def do_b(job):
    count = 0
    page = requests.get(job[1])

    if page.status_code == 204:  # Network stuff
        time.sleep(120)
        return 1

    t = html.fromstring(page.content)
    v = t.xpath('//div[@class="search-result__r1"]/div/a/@href')

    for a in v:
        ID = re.search('(?<=classified/advert/)[0-9]+', a)
        if ID:
            ID = int(ID.group(0))
            jlist.append(("a", ID))  # b jobs produce a jobs
            rlist.append([ID] + [None] * 17 + [int(time.time())] + [None])
            count += 1

    print("B " + str(count))
    return 0


def do_c(job):
    page = requests.get(job[1] + "1")
    if page.status_code == 204:  # Network stuff
        time.sleep(120)
        return 1

    t = html.fromstring(page.content)
    t.xpath('//div[@class="search-result__r1"]/div/a/@href')
    t_cars = t.xpath(
        '//h1[@class="search-form__count js-results-count"]/text()'
    )[0]
    t_cars = re.search('[0-9,]+', t_cars).group(0)
    t_cars = int(t_cars.replace(",", ""))
    pageno = t_cars // 10 + 1

    for i in range(pageno):
        jlist.append(("b", job[1] + str(i + 1)))  # c jobs produce b jobs

    print("C " + str(pageno))
    return 0


def updater():
    global jlist
    with sqlite3.connect('test.db') as conn:
        c = conn.cursor()
        now = int(time.time())
        cutoff = now - 60 * 60 * 24
        c.execute('SELECT url FROM cars WHERE last_seen < ?'
                  'AND first_gone IS NULL', [cutoff])
        alist = c.fetchall()

    # how this next line works is beyond me
    from_database = [item for sublist in alist for item in sublist]
    from_jlist = []
    clist = jlist

    for i in clist:
        if i[0] == 'a':
            from_jlist.append(i[1])

    to_add = list(set(from_database) - set(from_jlist))

    for i in to_add:
        jlist.append(['a', i])

    return len(to_add)


def combine_lines(olds, newline):
    """This combines lines (one line in newline, multiple in olds)"""
    final = newline
    for old in olds:
        final = combine_two(final, old)
    return final


def combine_two(newline, oldline):
    """ The bigger entries are kept for each field, except """
    """ for the last field, in which the smallest non-None entry is kept"""
    final = newline
    for i in range(len(final) - 1):
        final[i] = my_max(final[i], oldline[i])
    if not final[-1]:
        final[-1] = oldline[-1]
    elif oldline[-1]:
        final[-1] = min(final[-1], oldline[-1])
    return final


def my_max(one, two):
    if not one:
        return two
    if not two:
        return one
    if type(one) is str or type(two) is str:
        return(max(str(one), str(two)))
    else:
        return(max(one, two))


def jparse(data):
    if(data[0] == "a"):
        ret = [None] * 2
        ret[0] = "a"
        ret[1] = int(data[1:])
        return ret
    elif(data[0] == "b"):
        ret = [None] * 2
        ret[0] = "b"
        ret[1] = data[1:]
        return ret
    elif(data[0] == "c"):
        ret = [None] * 2
        ret[0] = "c"
        ret[1] = data[1:]
        return ret
    else:
        return 0


class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):

    def handle(self):
        global STAHP
        data = self.request.recv(1024).decode('UTF-8')
        if(data == 'shutdown'):
            STAHP = True
            self.request.sendall(b'shutting down')
            while(self.request.recv(1024)):
                pass
            return 0
        if data == 'updater':
            print('U ' + str(updater()))
            self.request.sendall(b'updatr')
            while(self.request.recv(1024)):
                pass
            return 0
        job = jparse(data)
        if job:
            jlist.append(job)
            self.request.sendall(b'added')
        else:
            self.request.sendall(b'not a correct command')
        while(self.request.recv(1024)):
            pass
        print("*")


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


global a_list, bc_list, r_list
a_list, bc_list, r_list = [], [], []
HOST, PORT = "localhost", 9500
STAHP = False   # How the main loop knows when to STAHP

server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)

ip, port = server.server_address

# Start a thread with the server -- that thread will then start one
# more thread for each request
server_thread = threading.Thread(target=server.serve_forever)

# Exit the server thread when the main thread terminates
server_thread.daemon = True
server_thread.start()

# This thread to move things from rlist to a sqlite3 database file
# Always running to avoid starting a new connection for each entry
sql_thread = threading.Thread(target=sql_writer)
sql_thread.daemon = True
sql_thread.start()

# Pay attention, this is the MAIN LOOP:
while not STAHP:
    time.sleep(random.gammavariate(.1, 1))

    if bc_list:
        job = random.choice(bc_list)
    else if a_list:
        job = random.choice(a_list)
    else:
        print("Z")
        time.sleep(10)
        continue

    status = do_job(job)

    if status == 0:
        if job[0] == 'a':
            a_list.remove(job)
        else:
            bc_list.remove(job)
    else:
        print(status, job)

# If we have unfinished jobs in jlist, that's pickled for later
# surely SOMEONE should import them at startup then
if(jlist):
    print('unfinished jobs in jlist', len(jlist))
    with open(str("jlist.txt"), "wb") as fl:
        pickle.dump(jlist, fl)

print('unwritten results in rlist', len(rlist))

server.shutdown()
server.server_close()
