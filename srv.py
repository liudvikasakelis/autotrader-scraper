import socket
import threading
import SocketServer
from time import sleep
import random
import pickle
import requests
import re
from lxml import html
import ff1
import sqlite3


def add_jlist(job):
    global jlock
    global jlist
    while jlock:
        sleep(random.uniform(0.01, 0.1))
    jlock = True
    jlist.append(job)
    jlock = False
    return 0


def add_rlist(result):
    global rlist
    global rlock
    while rlock:
        sleep(random.uniform(0.01, 0.1))
    rlock = True
    rlist.append(result)
    rlock = False
    return 0


def do_c(job):
    page = requests.get(job[1] + "1")
    if str(page) == '<Response [204]>':  # Network stuff
        sleep(120)
        return 1

    t = html.fromstring(page.content)
    t.xpath('//div[@class="search-result__r1"]/div/a/@href')
    t_cars = t.xpath(
        '//h1[@class="search-form__count js-results-count"]/text()'
    )[0]
    t_cars = re.search('[0-9,]+', t_cars).group(0)
    t_cars = int(t_cars.replace(",", ""))
    pageno = t_cars / 10 + 1

    for i in range(pageno):
        add_jlist(("b", job[1] + str(i + 1)))  # c jobs produce b jobs

    print("C " + str(pageno))
    return 0


def do_b(job):
    count = 0
    page = requests.get(job[1])

    # FIXME: page.status == 204
    if(str(page) == '<Response [204]>'):  # Network stuff
        sleep(120)
        return 1

    t = html.fromstring(page.content)
    v = t.xpath('//div[@class="search-result__r1"]/div/a/@href')

    for a in v:
        ID = re.search('(?<=classified/advert/)[0-9]+', a)
        if ID:
            ID = int(ID.group(0))
            add_jlist(("a", ID))  # b jobs produce a jobs
            count += 1

    print("B " + str(count))
    return 0


def do_a(job):
    global rlock
    global rlist
    result = ff1.scraper(job[1])

    if result[1] == 'AUTOTRADER_FAILED':
        print("Server failed")
        sleep(60)
        return 1

    while rlock:
        sleep(random.uniform(0.01, 0.1))
    rlock = True
    rlist.append(result)
    rlock = False
    print("A")
    return 0


def sql_writer():
    global STAHP
    global rlist
    global rlock
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
                while rlock:
                    sleep(random.uniform(0.01, 0.1))
                rlock = True
                rlist.remove(job)
                rlock = False
            conn.commit()
            sleep(5)


# This combines lines (one line in newline, multiple in olds)
def combine_lines(olds, newline):
    final = newline
    for old in olds:
        final = combine_two(final, old)
    return final


# The bigger entries are kept for each field
# except for the last field, in which the smallest non-None entry is kept
def combine_two(newline, oldline):
    final = newline
    for i in range(len(final) - 1):
        final[i] = max(final[i], oldline[i])
    if not final[-1]:
        final[-1] = oldline[-1]
    elif oldline[-1]:
        final[-1] = min(final[-1], oldline[-1])
    return final


def jparse(data):
    if(data[0] == "a"):
        ret = [None] * 2
        ret[0] = "a"
        try:
            ret[1] = int(data[1:])
        # FIXME: Undefined exception
        except Exception:
            return 0
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


class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):

    def handle(self):
        global STAHP
        data = self.request.recv(1024)
        if(data == 'shutdown'):
            STAHP = True
            self.request.sendall("shutting down")
            while(self.request.recv(1024)):
                pass
            return 0
        job = jparse(data)
        if job:
            status = add_jlist(job)
            if(status == 0):
                self.request.sendall("added")
            else:
                self.request.sendall("failed to add (%s)" % (status))
        else:
            self.request.sendall("not a correct command")
        while(self.request.recv(1024)):
            pass
        print("*")


class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass


jlock = False   # Lock to jlist
jlist = []      # Job list
rlock = False   # Lock to rlist
rlist = []      # Result list
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
    sleep(random.gammavariate(1, 1))
    if(jlist):
        job = random.choice(jlist)
        if(job[0] == "a"):
            status = do_a(job)
        elif(job[0] == "b"):
            status = do_b(job)
        elif(job[0] == "c"):
            status = do_c(job)

        if(status == 0):
            while jlock:
                sleep(random.uniform(0.01, 0.1))
            jlock = True
            jlist.remove(job)
            jlock = False
        else:
            print("job failed:")
            print(job)
            print("status: " + str(status))

# If we have unfinished jobs in jlist, that's pickled for later
# surely SOMEONE should import them at startup then
if(jlist):
    with open(str("jlist.txt"), "wb") as fl:
        pickle.dump(jlist, fl)

print(len(rlist))

server.shutdown()
server.server_close()
