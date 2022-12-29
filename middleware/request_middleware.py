
def ban_ip(request):
    """
    request属性和server的实现有关
    :param request:
    :return:
    """
    print(request.__dict__)
    if request.remote_addr.startswith('127'):
        return request
    else:
        return None
