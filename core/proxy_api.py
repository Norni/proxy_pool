from flask import Flask, request
from proxy_pool.utils.mongo_pool import MongoPool


class ProxyApi(object):

    def __init__(self):
        self.app = Flask(__name__)
        self.mongo_pool = MongoPool()

        @self.app.route('/random')
        def random_proxy():
            protocol = request.args.get('protocol')
            domain = request.args.get('domain')
            nick_type = request.args.get('nick_type')
            proxy = self.mongo_pool.get_one_random_proxy(protocol=protocol, nick_type=nick_type, domain=domain)
            if protocol:
                return "{}://{}:{}".format(proxy.protocol, proxy.ip, proxy.port)
            else:
                return "{}:{}".format(proxy.ip, proxy.port)

        @self.app.route('/proxies')
        def get_proxies():
            protocol = request.args.get('protocol')
            domain = request.args.get('domain')
            nick_type = request.args.get('nick_type')
            count = request.args.get('count')
            proxies = self.mongo_pool.get_proxies(protocol=protocol, nick_type=nick_type, domain=domain, count=count)
            proxies = [proxy.__dict__ for proxy in proxies]
            return json.dumps(proxies)

        @self.app.route('/disable_domain')
        def proxies():
            ip = request.args.get('ip')
            domain = request.args.get('domain')
            if ip is None:
                return "请提供ip参数"
            if domain is None:
                return "请提供domain参数"
            self.mongo_pool.add_disable_domain(ip, domain)
            return "{} 禁用域名 {} 成功".format(ip, domain)

    def run(self):
        self.app.run(host='192.168.0.106', port=8888)

    @classmethod
    def start(cls):
        rs = ProxyApi()
        rs.run()


if __name__ == "__main__":
    ProxyApi().start()
