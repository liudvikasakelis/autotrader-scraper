#!/usr/bin/python3

import socket


def client(message, HOST='localhost', PORT=9500):
    if not message:
        raise ValueError('message of length 0')
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))
    message = bytes(str(message), 'UTF-8')
    sock.sendall(message)
    reply = sock.recv(1024)
    sock.shutdown(0)
    sock.close()
    return reply.decode('UTF-8')


def add_query(price_from=0,
              price_to=100000,
              postcode='sy12dj',
              radius=200,
              make=None,
              **kwargs):
    url = 'http://www.autotrader.co.uk/car-search?'
    if postcode:
        url += 'postcode=' + postcode + '&'
    if radius:
        url += 'radius=' + str(radius) + '&'
    if price_from:
        url += 'price-from=' + str(price_from) + '&'
    if price_to:
        url += 'price-to=' + str(price_to) + '&'
    if make:
        url += 'make=' + str(make) + '&'
    url += '&page='
    client('c' + url, **kwargs)


def multiple_queries(price_from=0, price_to=100000, **kwargs):
    while price_from < price_to:
        add_query(price_from=price_from,
                  price_to=price_from + 500,
                  **kwargs)
        price_from = price_from + 500


def update(**kwargs):
    client('update', **kwargs)


def prune(**kwargs):
    client('prune', **kwargs)


def shutdown(**kwargs):
    client('shutdown', **kwargs)


def afd(**kwargs):
    client('afd', **kwargs)
