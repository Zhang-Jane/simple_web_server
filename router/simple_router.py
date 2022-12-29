import re


class SimpleRouter:
    route_table = []
    @classmethod
    def register(cls, method, pattern):
        def wrapper(handler):
            # 添加一个元祖进入有序列表
            cls.route_table.append(
                (method.upper(), re.compile(pattern), handler))
            return handler
        return wrapper
