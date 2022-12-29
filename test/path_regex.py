import re
regex = re.compile('/{([^{}:]+):?([^{}:]*)}')
s = [
    '/student/{name:str}/xxx/{id:int}',
    '/student/xxx/{id:int}/yyy',
    '/student/xxx/5134324',
    '/student/{name:}/xxx/{id}',
    '/student/{name:}/xxx/{id:aaa}'
]
# /{id:int} => /(?P<id>[+-]?\d+)
# '/(?<{}>{})'.format('id', TYPEPATTERNS['int'])
TYPEPATTERNS = {
    'str': r'[^/]+',
    'word': r'\w+',
    'int': r'[+-]?\d+',
    'float': r'[+-]?\d+\.\d+',  # 严苛的要求必须是 15.6这样的形式
    'any': r'.+'
}


def repl(matcher):
    # print(matcher.group(0))
    # print(matcher.group(1))
    # print(matcher.group(2)) # {name}或{name:}这个分组都匹配为''
    return '/(?P<{}>{})'.format(
        matcher.group(1),
        TYPEPATTERNS.get(matcher.group(2), TYPEPATTERNS['str'])
    )


def parse(src: str):
    return regex.sub(repl, src)


for x in s:
    print(parse(x))
