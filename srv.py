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
import sys

global a_list, bc_list, r_list
a_list, bc_list, r_list = [], [], []
HOST, PORT = "localhost", 9500
global STAHP
STAHP = False
global db_filename
db_filename = sys.argv[1]


def do_command(cmd):
    if cmd == 'shutdown':
        global STAHP
        STAHP = True
        return 'server shuts down'
    if cmd == 'update':
        return updater()
    if cmd == 'afd':
        return add_from_database()
    if cmd == 'a_status':
        return len(a_list)
    if cmd == 'bc_status':
        return len(bc_list)
    if cmd == 'r_status':
        return len(r_list)
    if cmd == 'a_flush':
        q = len(a_list)
        a_list.clear()
        return q
    if cmd == 'bc_flush':
        q = len(bc_list)
        bc_list.clear()
        return q
    return -1


def sql_writer():
    with sqlite3.connect(db_filename) as conn:
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
            while(r_list):
                job = r_list[0]
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
                r_list.remove(job)
            conn.commit()
            time.sleep(5)


def do_job(job):
    if job[0] == 'a':
        status = do_a(job)
    elif job[0] == 'b':
        status = do_b(job)
    elif job[0] == 'c':
        status = do_c(job)
    else:
        status = 4
    return status


def do_a(job):
    result = ff1.scraper(job[1])

    if result[1] == 'AUTOTRADER_FAILED':
        print("Server failed")
        return 1

    r_list.append(result)
    print("A")
    return 0


def do_b(job):
    count = 0
    car_ids = ff1.b_scraper(job[1])
    if car_ids == -1:
        return 1
    for ID in car_ids:
        a_list.append(("a", ID))  # b jobs produce a jobs
        r_list.append([ID] + [None] * 17 + [int(time.time())] + [None])
        count += 1
    print("B " + str(count))
    return 0


def do_c(job):
    pageno = ff1.c_scraper(job[1] + '1')
    if pageno == -1:
        return 1
    for i in range(pageno):
        bc_list.append(("b", job[1] + str(i + 1)))  # c jobs produce b jobs
    print("C " + str(pageno))
    return 0


def add_from_database():
    counter = 0
    with sqlite3.connect(db_filename) as conn:
        c = conn.cursor()
        c.execute('SELECT url FROM cars WHERE make IS NULL AND first_gone IS NULL')
        alist = c.fetchall()
    from_database = [item for sublist in alist for item in sublist]
    for element in from_database:
        a_list.append(['a', element])
        counter += 1
    return counter


def updater():
    with sqlite3.connect(db_filename) as conn:
        c = conn.cursor()
        now = int(time.time())
        cutoff = now - 60 * 60 * 24
        c.execute('SELECT url FROM cars WHERE last_seen < ?'
                  'AND first_gone IS NULL', [cutoff])
        alist = c.fetchall()

    # how this next line works is beyond me
    from_database = [item for sublist in alist for item in sublist]
    from_jlist = []
    clist = a_list

    for i in clist:
        if i[0] == 'a':
            from_jlist.append(i[1])

    to_add = list(set(from_database) - set(from_jlist))

    for i in to_add:
        a_list.append(['a', i])

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
    if data[1:8] != 'http://':
        return 0
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
        data = self.request.recv(1024).decode('UTF-8')
        ret = do_command(data)
        if ret != -1:
            self.request.sendall(str(ret).encode())
            while(self.request.recv(1024)):
                pass
            return 0
        job = jparse(data)
        if job:
            if job[0] == 'a':
                a_list.append(job)
            else:
                bc_list.append(job)
            self.request.sendall(b'added')
        else:
            self.request.sendall(b'not a correct command')
        while(self.request.recv(1024)):
            pass
        print("*")


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)

ip, port = server.server_address

# Start a thread with the server -- that thread will then start one
# more thread for each request
server_thread = threading.Thread(target=server.serve_forever)

# Exit the server thread when the main thread terminates
server_thread.daemon = True
server_thread.start()

# This thread to move things from r_list to a sqlite3 database file
# Always running to avoid starting a new connection for each entry
sql_thread = threading.Thread(target=sql_writer)
sql_thread.daemon = True
sql_thread.start()

# Pay attention, this is the MAIN LOOP:
while not STAHP:
    time.sleep(random.gammavariate(.1, 1))

    if bc_list:
        job = random.choice(bc_list)
    elif a_list:
        job = random.choice(a_list)
    else:
        print("Z")
        time.sleep(10)
        continue

    status = do_job(job)

    if status == 0:
        if job[0] == 'a':
            try:
                a_list.remove(job)
            except ValueError:
                pass
        else:
            try:
                bc_list.remove(job)
            except ValueError:
                pass
    else:
        if status == 1:   # Network things
            time.sleep(10)
        print(status, job)

# If we have unfinished jobs in jlist, that's pickled for later
# surely SOMEONE should import them at startup then
if(a_list):
    print('unfinished jobs in a_list', len(a_list))
    with open(str("alist.txt"), "wb") as fl:
        pickle.dump(a_list, fl)

print('unwritten results in r_list', len(r_list))

server.shutdown()
server.server_close()
