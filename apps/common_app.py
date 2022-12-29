from typing import Callable

from webob import Request
from webob.dec import wsgify
from webob.exc import HTTPNotFound, HTTPForbidden

from router.common_router import CommonRouter


class CommonApp:
    _ROUTERS = []  # 存储所有Router对象，有序列表
    _REQUEST_INTERCEPTOR = []


    # 注册路由
    @classmethod
    def register_router(cls, *routers: CommonRouter):
        for router in routers:
            cls._ROUTERS.append(router)

    # 注册拦截器
    @classmethod
    def register_intercept(cls, fn: Callable):
        cls._REQUEST_INTERCEPTOR.append(fn)
        return fn

    @wsgify
    def __call__(self, request: Request):
        # 请求拦截器
        for fn in self._REQUEST_INTERCEPTOR:
            request = fn(request)
        if not request:
            raise HTTPForbidden

        # 遍历_ROTERS，调用Router实例的match方法，看谁匹配
        for router in self._ROUTERS:
            response = router.match(request)
            if response:  # 匹配返回非None的Router对象
                return response  # 匹配则立即返回
        else:
            raise HTTPNotFound('<h1>你访问的页面被外星人劫持了</h1>')
