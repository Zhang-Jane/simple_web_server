import io
import socket
import sys
from datetime import datetime
# https://ruslanspivak.com/lsbaws-part2/
"""
It cannot accept a new connection until after it has finished processing a current client request. Some clients might be unhappy with it because they will have to wait in line, and for busy servers the line might be too long.
"""

class WSGIServer(object):
    """
    socket_family可以是如下参数：
    　　　　　　　　socket.AF_INET IPv4（默认）
    　　　　　　　　socket.AF_INET6 IPv6
    　　　　　　　　socket.AF_UNIX 只能够用于单一的Unix系统进程间通信
    socket_type可以是如下参数:
        socket.SOCK_STREAM　　流式socket , for TCP （默认）
        socket.SOCK_DGRAM　　 数据报式socket , for UDP
        socket.SOCK_RAW 原始套接字，普通的套接字无法处理ICMP、IGMP等网络报文，而SOCK_RAW可以；其次，SOCK_RAW也可以处理特殊的IPv4报文；此外，利用原始套接字，可以通过IP_HDRINCL套接字选项由用户构造IP头。
        socket.SOCK_RDM 是一种可靠的UDP形式，即保证交付数据报但不保证顺序。SOCK_RAM用来提供对原始协议的低级访问，在需要执行某些特殊操作时使用，如发送ICMP报文。SOCK_RAM通常仅限于高级用户或管理员运行的程序使用。
        socket.SOCK_SEQPACKET 可靠的连续数据包服务
    setsockopt:
    level:(级别)： 指定选项代码的类型。
        SOL_SOCKET: 基本套接口
        IPPROTO_IP: IPv4套接口
        IPPROTO_IPV6: IPv6套接口
        IPPROTO_TCP: TCP套接口
    opotion(See the Unix manual for level and option -- https://www.gnu.org/software/libc/manual/html_node/Socket_002dLevel-Options.html):
    协议层 选项名字 含义
    SOL_SOCKET SO_REUSEADDR 允许重用本地地址和端口
    SOL_SOCKET SO_KEEPALIVE 保持连接
    SOL_SOCKET SO_LINGER 延迟关闭连接
    SOL_SOCKET SO_BROADCAST 允许发送广播数据
    SOL_SOCKET SO_OOBINLINE 带外数据放入正常数据流
    SOL_SOCKET SO_SNDBUF 发送缓冲区大小
    SOL_SOCKET SO_RCVBUF 接收缓冲区大小
    SOL_SOCKET SO_TYPE 获得套接字类型
    SOL_SOCKET SO_ERROR 获得套接字错误
    SOL_SOCKET SO_DEBUG 允许调试
    SOL_SOCKET SO_RCVLOWAT 接收缓冲区下限
    SOL_SOCKET SO_SNDLOWAT 发送缓冲区下限
    SOL_SOCKET SO_RCVTIMEO 接收超时
    SOL_SOCKET SO_SNDTIMEO 发送超时
    SOL_SOCKET SO_BSDCOMPAT 与BSD系统兼容
    IPPROTO_IP IP_HDRINCL　　在数据包中包含IP首部
    IPPROTO_IP IP_OPTINOS　　　　IP首部选项　
    IPPROTO_IP IP_TOS　　　　　服务类型
    IPPROTO_IP IP_TTL　　　　　生存时间
    IPPRO_TCP TCP_MAXSEG　　TCP最大数据段的大小
    IPPRO_TCP TCP_NODELAY　　不使用Nagle算法

    """

    address_family = socket.AF_INET
    socket_type = socket.SOCK_STREAM
    request_queue_size = 100

    def __init__(self, server_address):
        # Create a listening socket
        self.listen_socket = listen_socket = socket.socket(
            self.address_family,
            self.socket_type
        )
        # Allow to reuse the same address
        listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Bind
        listen_socket.bind(server_address)
        # Activate,backlog：it specifies the number of unaccepted connections that the system will allow before refusing new connections. If not specified, a default reasonable value is chosen.
        listen_socket.listen(self.request_queue_size)
        # Get server host name and port
        host, port = self.listen_socket.getsockname()[:2]
        self.server_name = socket.getfqdn(host)
        self.server_port = port
        # Return headers set by Web framework/Web application
        self.headers_set = []

    def set_app(self, application):
        self.application = application

    def serve_forever(self):
        listen_socket = self.listen_socket
        while True:
            # New client connection
            self.client_connection, client_address = listen_socket.accept()
            # Handle one request and close the client connection. Then
            # loop over to wait for another client connection
            self.handle_one_request()
            print(f'Server received connection'
                  f' from {client_address}')

    def handle_one_request(self):
        request_data = self.client_connection.recv(1024)
        print(request_data)
        self.request_data = request_data = request_data.decode('utf-8')
        # Print formatted request data a la 'curl -v'
        print(''.join(
            f'< {line}\n' for line in request_data.splitlines()
        ))

        self.parse_request(request_data)

        # Construct environment dictionary using request data
        env = self.get_environ()

        # It's time to call our application callable and get
        # back a result that will become HTTP response body
        result = self.application(env, self.start_response)

        # Construct a response and send it back to the client
        self.finish_response(result)

    def parse_request(self, text):
        request_line = text.splitlines()[0]
        request_line = request_line.rstrip('\r\n')
        # Break down the request line into components
        (self.request_method,  # GET
         self.path,            # /hello
         self.request_version  # HTTP/1.1
         ) = request_line.split()

    def get_environ(self):
        env = {}
        # The following code snippet does not follow PEP8 conventions
        # but it's formatted the way it is for demonstration purposes
        # to emphasize the required variables and their values
        #
        # Required WSGI variables
        env['wsgi.version'] = (1, 0)
        env['wsgi.url_scheme'] = 'http'
        env['wsgi.input'] = io.StringIO(self.request_data)
        env['wsgi.errors'] = sys.stderr
        env['wsgi.multithread'] = False
        env['wsgi.multiprocess'] = False
        env['wsgi.run_once'] = False
        # Required CGI variables
        env['REQUEST_METHOD'] = self.request_method    # GET
        env['PATH_INFO'] = self.path              # /hello
        env['SERVER_NAME'] = self.server_name       # localhost
        env['SERVER_PORT'] = str(self.server_port)  # 8888
        return env

    def start_response(self, status, response_headers, exc_info=None):
        # Add necessary server headers
        server_headers = [
            ('Date', datetime.now()),
            ('Server', 'WSGIServer 0.2'),
        ]
        self.headers_set = [status, response_headers + server_headers]
        # To adhere to WSGI specification the start_response must return
        # a 'write' callable. We simplicity's sake we'll ignore that detail
        # for now.
        # return self.finish_response

    def finish_response(self, result):
        try:
            status, response_headers = self.headers_set
            response = f'HTTP/1.1 {status}\r\n'
            for header in response_headers:
                response += '{0}: {1}\r\n'.format(*header)
            response += '\r\n'
            for data in result:
                response += data.decode('utf-8')
            # Print formatted response data a la 'curl -v'
            print(''.join(
                f'> {line}\n' for line in response.splitlines()
            ))
            response_bytes = response.encode()
            self.client_connection.sendall(response_bytes)
        finally:
            self.client_connection.close()


SERVER_ADDRESS = (HOST, PORT) = '', 8888


def make_server(server_address, application):
    server = WSGIServer(server_address)
    server.set_app(application)
    return server


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit('Provide a WSGI application object as module:callable')
    app_path = sys.argv[1]
    module, application = app_path.split(':')
    module = __import__(module)
    application = getattr(module, application)
    httpd = make_server(SERVER_ADDRESS, application)
    print(f'WSGIServer: Serving HTTP on port {PORT} ...\n')
    httpd.serve_forever()
