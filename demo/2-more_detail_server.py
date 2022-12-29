from wsgiref.simple_server import make_server
import webob
from webob.dec import wsgify
server_ip = "127.0.0.1"
port = 9991


def html():
    text = "<h1>你好</h1>".encode("utf-8")
    return text

def handle_app(environ: dict) -> webob.Response:
    request_para = webob.Request(environ)
    print(request_para)
    """
    GET /?name=jane HTTP/1.1
    Accept: */*
    Accept-Encoding: gzip, deflate
    Connection: keep-alive
    Content-Length: 
    Content-Type: text/plain
    Host: 127.0.0.1:9991
    User-Agent: HTTPie/3.2.1
    """
    response = webob.Response()
    response.body = html()

    return  response


# 自己实现application
def simple_app(environ, start_response):
    """Simplest possible application object"""
    # 处理environ
    response = handle_app(environ)
    return response(environ, start_response)

@wsgify
def simple_app2(request: webob.Request) -> webob.Response:
    print(request)
    res = webob.Response("<h1>你好</h1>")
    return res



server = make_server(server_ip, port, simple_app2)

server.serve_forever()  # handle_request() 一次
