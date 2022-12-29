# coding=utf-8

import socket

listener = socket.socket()
listener.setsockopt(socket.SOL_SOCKET,
                    socket.SO_REUSEADDR, 1)
listener.bind(('0.0.0.0', 8080))
listener.listen(1)
print('Serving HTTP on 0.0.0.0 port 8080 ...')

while True:
    client_connection, client_address = \
        listener.accept()
    print(f'Server received connection'
          f' from {client_address}')
    request = client_connection.recv(1024)
    print(f'request we received: {request}')

    response = b"""
        HTTP/1.1 200 OK
        
        Hello, World!
        """
    client_connection.sendall(response)
    client_connection.close()