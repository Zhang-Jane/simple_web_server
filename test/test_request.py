import threading
import time
import logging
import requests

logging.basicConfig(
    level=logging.INFO,
    format="%(process)d %(processName)s %(thread)d %(message)s")
log = logging


def get_download(i):

    s = requests.get(url=f"http://127.0.0.1:9999/home/{i}")
    print(s.url)
    return s.status_code


if __name__ == '__main__':
    start = time.time()
    print('这是主线程：{}'.format(threading.current_thread().name))
    thread_list = []
    for i in range(10):
        t = threading.Thread(target=get_download, args=(i,))
        thread_list.append(t)

    for t in thread_list:
        t.start()

    for t in thread_list:
        t.join()

    end = time.time()
    print("总共用时{}秒".format((end - start)))
