from pymongo import MongoClient
import pymongo
import random
from proxy_pool.settings import MONGO_URL
from proxy_pool.utils.proxy_module import Proxy
from proxy_pool.utils.log import logger


class MongoPool(object):

    def __init__(self):
        self.mongo_client = MongoClient(MONGO_URL)
        self.proxies = self.mongo_client['proxy_pool']['proxies']

    def __del__(self):
        self.mongo_client.close()

    def insert_one(self, proxy):
        count = self.proxies.count({"_id": proxy.ip})
        if count == 0:
            data = proxy.__dict__
            data['_id'] = proxy.ip
            self.proxies.insert_one(data)
            logger.info('插入新的代理：{}'.format(proxy))
        else:
            logger.warning('该代理已存在：{}'.format(proxy.ip))

    def delete_one(self, proxy):
        count = self.proxies.count({'_id': proxy.ip})
        if count == 1:
            self.proxies.delete_one({'_id': proxy.ip})
            logger.warning('已删除代理：{}'.format(proxy))
        else:
            logger.info('该代理：{}不存在'.format(proxy.ip))

    def update_one(self, proxy):
        count = self.proxies.count({'_id': proxy.ip})
        if count == 1:
            self.proxies.update_one({'_id': proxy.ip}, {"$set": proxy.__dict__})
            logger.info('已更新代理：{}'.format(proxy))
        else:
            logger.info('该代理：{}不存在'.format(proxy.ip))

    def find_all(self):
        proxies = self.proxies.find()
        for item in proxies:
            item.pop('_id')
            proxy = Proxy(**item)
            yield proxy

    def find_sort(self, conditions, count=0):
        proxies = self.proxies.find(filter=conditions, limit=count).sort(
            [("score", pymongo.DESCENDING), ('speed', pymongo.ASCENDING)])
        for item in proxies:
            item.pop("_id")
            proxy = Proxy(**item)
            yield proxy

    def get_proxies(self, protocol=None, nick_type=0, domain=None, count=0):
        conditions = {
            'nick_type': nick_type
        }
        if protocol is None:
            conditions['protocol'] = 2
        elif protocol.lower() == "https":
            conditions['protocol'] = {'$in': [1, 2]}
        else:
            conditions['protocol'] = {'$in': [0, 2]}
        if domain:
            conditions['disable_domain'] = {"$nin": [domain]}
        proxy_list = list()
        for proxy in self.find_sort(conditions=conditions, count=count):
            proxy_list.append(proxy)
        return proxy_list

    def get_one_random_proxy(self, protocol=None, nick_type=0, domain=None, count=0):
        return random.choice(self.get_proxies(protocol=protocol, nick_type=nick_type, domain=domain, count=count))

    def add_disable_domain(self, ip, domain):
        count = self.proxies.count({"_id": ip})
        if count == 1:
            self.proxies.update_one({"_id": ip}, {"$push": {"disable_domain": domain}})
            return True
        return False


if __name__ == "__main__":
    mongo_pool = MongoPool()
    # proxy = Proxy(ip='192.0.0.1', port=221)
    proxies = mongo_pool.find_all()
    for proxy in proxies:
        print(proxy)
