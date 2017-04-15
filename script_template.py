#!/usr/bin/python3
import time
import sys
A_PATH = ''
sys.path.append(A_PATH)
import client

PORT = 9500
postcode = ''
radius = 0
price_from = 0
price_to = 0

client.multiple_queries(postcode=postcode,
                        radius=radius,
                        price_from=price_from,
                        price_to=price_to)

while int(client.client('localhost', PORT, 'bc_status')) > 0:
    time.sleep(3)
print('flushing a_list')
client.client('localhost', PORT, 'a_flush')
time.sleep(1)
client.client('localhost', PORT, 'afd')
time.sleep(1)
client.client('localhost', PORT, 'update')
while int(client.client('localhost', PORT, 'a_status')) > 0:
    time.sleep(3)
print('afd and update complete')
client.client('localhost', PORT, 'shutdown')
