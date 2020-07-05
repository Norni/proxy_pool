from gevent import monkey
monkey.patch_all()

from gevent.pool import Pool
from queue import Queue
from proxy_pool.utils.mongo_pool import MongoPool
from proxy_pool.settings import ASYNC_COUNT, DEFAULT_SCORE, TEST_SPIDER_INTERVAL
from proxy_pool.utils.http_validate import check_proxy
import schedule
import time


class ProxyTest(object):
    def __init__(self):
        self.mongo_pool = MongoPool()
        self.proxy_queue = Queue()
        self.coroutine_pool = Pool()

    def check_one_proxy(self):
        proxy = self.proxy_queue.get()
        check_proxy(proxy)
        if proxy.speed == -1:
            proxy.score -= 1
            if proxy.score == 0:
                self.mongo_pool.delete_one(proxy)
            self.mongo_pool.update_one(proxy)
        proxy.score = DEFAULT_SCORE
        self.mongo_pool.update_one(proxy)
        self.proxy_queue.task_done()

    def check_call_back(self, temp):
        self.coroutine_pool.apply_async(func=self.check_one_proxy, callback=self.check_call_back)

    def run(self):
        for proxy in self.mongo_pool.find_all():
            self.proxy_queue.put(proxy)
        for i in range(ASYNC_COUNT):
            self.coroutine_pool.apply_async(func=self.check_one_proxy, callback=self.check_call_back)
        self.coroutine_pool.join()
        self.proxy_queue.join()

    @classmethod
    def start(cls):
        rs = cls()
        rs.run()
        schedule.every(TEST_SPIDER_INTERVAL).hours.do(rs.run)
        while True:
            schedule.run_pending()
            time.sleep(1)

if __name__ == "__main__":
    obj = ProxyTest()
    obj.start()
