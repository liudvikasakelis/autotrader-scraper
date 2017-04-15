#!/usr/bin/python3
import time
import sys
A_PATH = ''
sys.path.append(A_PATH)
import client

PORT = 9500
HOST = 'localhost'
postcode = ''
radius = 0
price_from = 0
price_to = 0

client.multiple_queries(postcode=postcode,
                        radius=radius,
                        price_from=price_from,
                        price_to=price_to,
                        HOST=HOST,
                        PORT=PORT)

while int(client.client('bc_status', HOST=HOST, PORT=PORT)) > 0:
    time.sleep(3)
print('flushing a_list')
client.client('a_flush', HOST=HOST, PORT=PORT)
time.sleep(1)
client.client('afd', HOST=HOST, PORT=PORT)
time.sleep(1)
client.client('update', HOST=HOST, PORT=PORT)
while int(client.client('a_status', HOST=HOST, PORT=PORT)) > 0:
    time.sleep(3)
print('afd and update complete')
client.client('shutdown', HOST=HOST, PORT=PORT)
