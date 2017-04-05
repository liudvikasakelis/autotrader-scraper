#!/usr/bin/python3

import socket


def client(HOST, PORT, message):
    if not message:
        raise ValueError('message of length 0')
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))
    message = bytes(str(message), 'UTF-8')
    sock.sendall(message)
    reply = sock.recv(1024)
    print("server says: " + reply.decode('UTF-8'))
    sock.shutdown(0)
    sock.close()


def add_query(postcode, radius, price_from, price_to):
    url = (
        'http://www.autotrader.co.uk/car-search?postcode={postcode}&radius='
        '{radius}&price-from={price_from}&price-to={price_to}&page='.format(
            postcode=postcode,
            radius=radius,
            price_from=price_from,
            price_to=price_to
        )
    )
    client('localhost', 9500, 'c' + url)


def multiple_queries(postcode, radius, price_from, price_to):
    while price_from < price_to:
        add_query(postcode, radius, price_from, price_from + 500)
        price_from = price_from + 500


def update():
    client('localhost', 9500, 'update')


def prune():
    client('localhost', 9500, 'prune')


def shutdown():
    client('localhost', 9500, 'shutdown')


def afd():
    client('localhost', 9500, 'afd')
