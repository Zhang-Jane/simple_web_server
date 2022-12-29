from webob import Request

import re


class AttrDict:
    def __init__(self, d: dict):
        self.__dict__.update(d if isinstance(d, dict) else {})

    def __setattr__(self, key, value):
        # 不允许修改属性
        raise NotImplementedError

    def __repr__(self):
        return "<AttrDict {}>".format(self.__dict__)

    def __len__(self):
        return len(self.__dict__)


class CommonRouter:
    # 正则转换
    __regex = re.compile(r'/{([^{}:]+):?([^{}:]*)}')
    TYPEPATTERNS = {
        'str': r'[^/]+',
        'word': r'\w+',
        'int': r'[+-]?\d+',
        'float': r'[+-]?\d+\.\d+',  # 严苛的要求必须是 15.6这样的形式
        'any': r'.+'
    }
    TYPECAST = {
        'str': str,
        'word': str,
        'int': int,
        'float': float,
        'any': str
    }

    def __parse(self, src: str):
        start = 0
        repl = ''
        types = {}
        matchers = self.__regex.finditer(src)
        for i, matcher in enumerate(matchers):
            name = matcher.group(1)
            types[name] = self.TYPECAST.get(matcher.group(2), str)
            repl += src[start:matcher.start()]  # 拼接分组前
            # 分组命名的规则为：（？<name>分组正则表达式）
            tmp = '/(?P<{}>{})'.format(
                matcher.group(1),
                self.TYPEPATTERNS.get(
                    matcher.group(2), self.TYPEPATTERNS['str'])
            )
            repl += tmp  # 替换
            start = matcher.end()  # 移动
        else:
            repl += src[start:]  # 拼接分组后的内容
        return repl, types

    def __init__(self, prefix: str = ''):
        self.__prefix = prefix.rstrip('/\\')  # 前缀，例如/product
        self.__routetable = []  # 存四元组，列表，有序的

    def route(self, rule, *methods):  # 注册路由，装饰器
        """
        路由的规则，比如{id:int} /123
        :param rule:
        :param methods:
        :return:
        """
        def wrapper(handler):
            # /student/{name:str}/xxx/{id:int} =>
            # '/student/(?P<name>[^/]+)/xxx/(?P<id>[+-]?\\d+)'
            pattern, trans = self.__parse(rule)  # 用户输入规则转换为正则表达式
            self.__routetable.append(
                (tuple(map(lambda x: x.upper(), methods)),
                 re.compile(pattern),  # 编译
                 trans,
                 handler)
            )  # (方法元组,预编译正则对象,类型转换,处理函数)
            return handler
        return wrapper

    def get(self, pattern):
        return self.route(pattern, 'GET')

    def post(self, pattern):
        return self.route(pattern, 'POST')

    def head(self, pattern):
        return self.route(pattern, 'HEAD')

    def match(self, request: Request):
        print(
            f"request.path is {request.path},  root path is {self.__prefix}", )
        # 必须先匹配前缀根路径
        if not request.path.startswith(self.__prefix):
            return None
        # 前缀匹配，说明就必须这个Router实例处理，后续匹配不上，依然返回None
        for methods, pattern, trans, handler in self.__routetable:
            # not methods表示一个方法都没有定义，就是支持全部方法
            if not methods or request.method.upper() in methods:
                # 前提已经是以__prefix开头了，可以replace，去掉prefix剩下的才是正则表达式需要匹配的路径
                next_path = request.path.replace(self.__prefix, '', 1)
                print(
                    f"替换的路径：{self.__prefix}, 替换之后的路径：{next_path}, 匹配的规则：{pattern}")
                matcher = pattern.match(next_path)
                if matcher:  # 正则匹配
                    newdict = {}
                    for k, v in matcher.groupdict().items():  # 命名分组组成的字典
                        newdict[k] = trans[k](v)
                        # 动态为request增加属性
                    request.vars = AttrDict(newdict)  # 属性化
                    return handler(request)
