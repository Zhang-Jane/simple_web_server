from wsgiref.simple_server import make_server, demo_app

HELLO_WORLD = "你好\n".encode("utf-8")
server_ip = "127.0.0.1"
port = 9991


class AppClass:
    """
    AppClass()会返回一个AppClass类对象作为application，而后在迭代的时候就会调用__iter__办法，而后就能够产生雷同的输入。
    如果咱们也能够实现__call__办法间接将实例当做application
    environ：environ参数是一个字典对象，该对象必须是内置的Python字典，应用程序能够任意批改该字典。字典还必须蕴含某些WSGI必须的变量。
    start_response：由server提供的回调函数，其作用是由application将状态码和响应头返回给server。这个函数有两个必须的地位参数和一个可选参数，三个参数别离为status，response_headers和exc_info
    """

    def __init__(self, environ, start_response):
        self.environ = environ
        self.start = start_response

    def __iter__(self):
        status = '200 OK'
        response_headers = [('Content-type', 'text/plain')]
        self.start(status, response_headers)
        yield "Hello world!\n"

# 自己实现application
def simple_app(environ, start_response):
    """Simplest possible application object"""
    status = '200 OK'
    response_headers = [('Content-type', 'text/plain')]
    start_response(status, response_headers)
    return [HELLO_WORLD]


server = make_server(server_ip, port, simple_app)

server.serve_forever()  # handle_request() 一次
