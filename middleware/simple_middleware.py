from wsgiref.simple_server import make_server


def application(environ, start_response):
    response_body = 'hello world!'.encode()

    status = '200 OK'

    response_headers = [
        ('Content-Type', 'text/plain'),
        ('Content-Length', str(len(response_body)))
    ]

    start_response(status, response_headers)
    return [response_body]


# 中间件
class UpperMiddleware:
    def __init__(self, app):
        self.wrapped_app = app

    def __call__(self, environ, start_response):
        for data in self.wrapped_app(environ, start_response):
            yield data.upper()


wrapped_app = UpperMiddleware(application)

httpd = make_server('localhost', 8051, wrapped_app)

httpd.serve_forever()
