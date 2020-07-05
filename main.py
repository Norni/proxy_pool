import sys

sys.path.append('../')

from multiprocessing import Process
from proxy_pool.core.run_spider import RunSpider
from proxy_pool.core.proxy_test import ProxyTest
from proxy_pool.core.proxy_api import ProxyApi


def run():
    process_list = list()
    process_list.append(Process(target=RunSpider.start))
    process_list.append(Process(target=ProxyTest.start))
    process_list.append(Process(target=ProxyApi.start))

    for process in process_list:
        process.daemon = True
        process.start()

    for process in process_list:
        process.join()


if __name__ == "__main__":
    run()
