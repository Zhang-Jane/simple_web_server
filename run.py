# from wsgiref.simple_server import make_server
from server.wsgi_server import WSGIServer
from apps.demo_app import DemoApp
server_ip = "127.0.0.1"
port = 8888
SERVER_ADDRESS = (HOST, PORT) = '', 9999

def main():
    # server = make_server(server_ip, port, DemoApp())
    server = WSGIServer()
    server.set_app(DemoApp())
    server.serve_forever()  # handle_request() 一次


if __name__ == '__main__':
    main()