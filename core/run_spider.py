from gevent import monkey

monkey.patch_all()
import importlib
from gevent.pool import Pool
from proxy_pool.settings import SPIDER_LIST, RUN_SPIDER_INTERVAL
from proxy_pool.utils.http_validate import check_proxy
from proxy_pool.utils.mongo_pool import MongoPool
from proxy_pool.utils.log import logger
import schedule
import time


class RunSpider(object):
    def __init__(self):
        self.mongo_pool = MongoPool()
        self.coroutine_pool = Pool()

    def get_spider_from_settings(self):
        for class_full_name in SPIDER_LIST:
            module_name, class_name = class_full_name.rsplit('.', 1)
            module = importlib.import_module(module_name)
            spider_class = getattr(module, class_name)
            spider = spider_class()
            yield spider

    def process_one_spider(self, spider):
        try:
            for proxy in spider.run():
                check_proxy(proxy)
                if proxy.speed != -1:
                    self.mongo_pool.insert_one(proxy)
        except Exception as ex:
            logger.warning(ex)

    def run(self):
        spider_list = self.get_spider_from_settings()
        for spider in spider_list:
            self.coroutine_pool.apply_async(func=self.process_one_spider, args=(spider,))
        self.coroutine_pool.join()

    @classmethod
    def start(cls):
        rs = cls()
        rs.run()
        schedule.every(RUN_SPIDER_INTERVAL).hours.do(rs.run)
        while True:
            schedule.run_pending()
            time.sleep(1)


if __name__ == "__main__":
    RunSpider().run()
