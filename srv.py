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


def addtojlist(job):
    global jlock
    global jlist
    while jlock:
        sleep(random.uniform(0.01, 0.1))
    jlock = True
    try:
        jlist.append(job)
        jlock = False
        return 0
    except:
        jlock = False
        return 1
      
def do_c(job):
    global jlock    
    global jlist
    page = requests.get(job[1]+"1") 
    t = html.fromstring(page.content) 
    v = t.xpath('//div[@class="search-result__r1"]/div/a/@href') 
    t_cars = t.xpath('//h1[@class="search-form__count js-results-count"]/text()')[0]
    t_cars = re.search('[0-9,]+', t_cars).group(0)
    t_cars = int(t_cars.replace(",", "")) 
    pageno = t_cars/10 + 1
    while jlock:
        sleep(random.uniform(0.01, 0.1))
    jlock = True
    for i in range(pageno):
        jlist.append(("b", job[1] + str(i+1)))
    jlock = False
    print("C " + str(pageno))
    return 0

def do_b(job):
    global jlock
    global jlist
    count = 0
    page = requests.get(job[1])
    t = html.fromstring(page.content)
    v = t.xpath('//div[@class="search-result__r1"]/div/a/@href')
    while jlock:
        sleep(random.uniform(0.01, 0.1))
    jlock = True
    for a in v:
        ID = re.search('(?<=classified/advert/)[0-9]+', a)
        if(ID):
            ID = int(ID.group(0))
            jlist.append(("a", ID))
            count += 1    
    jlock = False
    print("B " + str(count))
    return 0

def do_a(job):
    global rlock
    global rlist    
    result = ff1.scraper(job[1])
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
    with sqlite3.connect("test.db") as conn:    
        c = conn.cursor()
        while not STAHP:
            if(rlist):
                job = rlist[0]
                c.execute("SELECT * FROM cars WHERE url=?", [job[0]])
                match = c.fetchall()
                if(match):
                    final = combine_lines(match, job)
                else:
                    final = job
                c.execute("DELETE FROM cars WHERE url=?", [job[0]])
                c.execute("INSERT INTO cars VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                          final)
                conn.commit()
                while rlock:
                    sleep(random.uniform(0.01, 0.1))
                rlock = True 
                rlist.remove(job)
                rlock = False
            sleep(0.1)


def combine_lines(olds, newline):
    final = newline
    for old in olds:
        for i in range(len(old)-1):
            final[i] = max(final[i], old[i])  
        if not final[-1]:
            final[-1] = old[-1]
        elif old[-1]:
            final[-1] = min(final[-1], old[-1])
    return final 
                

def jparse(data):
    if(data[0] == "a"):
        ret = [None] * 2
        ret[0] = "a"
        try:
            ret[1] = int(data[1:])
        except:
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
        if(data=='shutdown'):
            STAHP = True
            self.request.sendall("shutting down")
            while(self.request.recv(1024)):
                pass             
            return 0
        job = jparse(data)
        if job:
            status = addtojlist(job)
            if(status == 0):
                self.request.sendall("added")
            else:
                self.request.sendall("failed to add (%s)"%(status))
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
            print("status: "+ str(status))

# If we have unfinished jobs in jlist, that's pickled for later
if(jlist):  
    with open(str("jlist.txt"), "wb") as fl:
        pickle.dump(jlist, fl)

# Print how far we got 
print(len(rlist))

server.shutdown()
server.server_close()
