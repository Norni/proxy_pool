import requests
import time
import json
from proxy_pool.utils.random_useragent import RandomUserAgent
from proxy_pool.utils.log import logger
from proxy_pool.settings import REQUEST_TIMEOUT
from proxy_pool.utils.proxy_module import Proxy


class HttpValidate(object):

    def _check_proxies(self, proxies, is_http=True):
        if is_http:
            test_url = 'http://httpbin.org/get'
        else:
            test_url = "https://httpbin.org/get"
        start_time = time.time()
        speed = -1
        nick_type = -1
        try:
            headers = {
                "User-Agent": "{}".format(RandomUserAgent())
            }
            response = requests.get(url=test_url, headers=headers, proxies=proxies, timeout=REQUEST_TIMEOUT)
            if response.ok:
                speed = time.time() - start_time
                data = json.loads(response.content.decode())
                print(data)
                headers = data["headers"]
                ip = data['origin']
                proxy_connection = headers.get('Proxy-Connection', None)
                if "," in ip:
                    nick_type = 2
                elif proxy_connection:
                    nick_type = 1
                else:
                    nick_type = 0
                return True, nick_type, speed
            return False, nick_type, speed
        except Exception as e:
            return False, nick_type, speed

    def check_proxy(self, proxy):
        proxies = {
            "http": "http://{}:{}".format(proxy.ip, proxy.port),
            "https": "https://{}:{}".format(proxy.ip, proxy.port)
        }
        is_http, http_nick_type, http_speed = self._check_proxies(proxies, is_http=True)
        is_https, https_nick_type, https_speed = self._check_proxies(proxies, is_http=False)
        if is_http and is_https:
            proxy.protocol = 2
            proxy.nick_type = https_nick_type
            proxy.speed = https_speed
        elif is_https:
            proxy.protocol = 1
            proxy.nick_type = https_nick_type
            proxy.speed = https_speed
        elif is_http:
            proxy.protocol = 0
            proxy.nick_type = http_nick_type
            proxy.speed = http_speed
        else:
            proxy.protocol = -1
            proxy.nick_type = -1
            proxy.speed = -1


def check_proxy(proxy):
    HttpValidate().check_proxy(proxy)


if __name__ == "__main__":
    proxy = Proxy(ip="159.203.44.177", port="3128")
    check_proxy(proxy)
    print(proxy)
