import webob
from webob.dec import wsgify
from router.simple_router import SimpleRouter


class DemoApp:
    @wsgify
    def __call__(self, request: webob.Request):
        for method, pattern, handler in SimpleRouter.route_table:
            if request.method.upper() != method:
                continue
            try:
                matched = pattern.match(request.path)
                # 将匹配到的分组传递给request对象
                if matched:
                    request.groups = matched.groups()
                    request.groupdict = matched.groupdict()
                    return handler(request)
            except Exception as e:
                print(e)

@SimpleRouter.register("get", "/")
def base_handler(request):
    return "hello"
