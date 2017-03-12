import socket


def client(HOST, PORT, message):
    if not message:
        raise ValueError('message of length 0')
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))
    sock.sendall(str(message))
    reply = sock.recv(1024)
    print("server says: " + reply)
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


def shutdown():
    client('localhost', 9500, 'shutdown')
