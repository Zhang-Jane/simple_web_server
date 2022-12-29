 # coding=utf-8

import socket
import sys


class WSGIServer:
    def __init__(self, ip="0.0.0.0", port=8888):
        self.listener = socket.socket()
        self.listener.setsockopt(socket.SOL_SOCKET,
                                 socket.SO_REUSEADDR, 1)
        self.listener.bind((ip, port))
        self.listener.listen(1)
        print(f'Serving HTTP on {ip} port {port} ...')
        self.app = None
        self.headers_set = None

    def set_app(self, application):
        self.app = application

    def start_response(self, status, headers):
        self.headers_set = [status, headers]

    def serve_forever(self):
        while True:
            listener = self.listener
            client_connection, client_address = \
                listener.accept()
            print(f'Server received connection'
                  f' from {client_address}')
            request = client_connection.recv(1024)
            print(f'request we received: {request}')

            method, path, _ = request.split(b' ', 2)
            # 如果有需要，可以自行完善
            environ = {
                'wsgi.version': (1, 0),
                'wsgi.url_scheme': 'http',
                'wsgi.input': request,
                'wsgi.errors': sys.stderr,
                'wsgi.multithread': False,
                'wsgi.multiprocess': False,
                'wsgi.run_once': False,
                'REQUEST_METHOD': method.decode('utf-8'),
                'PATH_INFO': path.decode('utf-8'),
                'SERVER_NAME': '127.0.0.1',
                'SERVER_PORT': '8080',
            }
            app_result = self.app(environ, self.start_response)

            response_status, response_headers = self.headers_set
            response = f'HTTP/1.1 {response_status}\r\n'
            for header in response_headers:
                response += f'{header[0]}: {header[1]}\r\n'
            response += '\r\n'
            response = response.encode('utf-8')
            for data in app_result:
                response += data

            client_connection.sendall(response)
            client_connection.close()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit('Argv Error')
    app_path = sys.argv[1]
    module, app = app_path.split(':')
    module = __import__(module)
    app = getattr(module, app)

    server = WSGIServer()
    server.set_app(app)
    server.serve_forever()