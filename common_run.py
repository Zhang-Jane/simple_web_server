# from wsgiref.simple_server import make_server
import time
from apps.common_app import CommonApp
from server.multi_server import make_server
from middleware.request_middleware import ban_ip
from router.common_router import CommonRouter
from webob import Response

"""
当我们去 import 一个 Package 的时候，它会隐性的去执行 __init__.py
"""

# 创建Router对象
router = CommonRouter()
# 初始化一级路由
second_router = CommonRouter('/home')
# 注册
CommonApp.register_router(router, second_router)
# CommonApp.register_intercept(ban_ip)


@second_router.route(r'^/{id:str}$')  # 支持所有方法访问
def index_handler(request):
    id = ''
    if request.vars:
        id = request.vars.id
        print(type(id))
        # time.sleep(3)
        return '<h1>北京欢迎你{}. beijing</h1>'.format(id)


@second_router.get('^/about$')
def about_handler(request):
    if request.vars:
        print(type(request.vars.id))
    res = Response()
    res.charset = 'utf-8'
    res.body = '<h1>About me</h1>'.encode()
    return res


if __name__ == '__main__':
    SERVER_ADDRESS = (HOST, PORT) = '', 9999
    ip = '127.0.0.1'
    port = 9999
    httpd = make_server(SERVER_ADDRESS, CommonApp())
    print('WSGIServer: Serving HTTP on port {port} ...\n'.format(port=PORT))
    httpd.serve_forever()

