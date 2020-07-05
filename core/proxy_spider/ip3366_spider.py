import requests
import re
import random
import time
from lxml import etree
from proxy_pool.utils.random_useragent import RandomUserAgent
from proxy_pool.utils.proxy_module import Proxy


class Ip3366ProxySpider(object):

    def __init__(self, first_url):
        self.first_url = first_url

    def construct_url(self, first_url):
        url_list = list()
        for num in range(1, 8):
            url = first_url + "&page=" + str(num)
            url_list.append(url)
        return url_list

    def construct_headers(self, url):
        if url.rsplit('=', 1)[-1] == '1':
            referer = None
        else:
            num = int(url.rsplit('=', 1)[-1])
            referer = re.sub(r'page=\d+', str(num - 1), url)
        headers = {
            "User-Agent": "{}".format(RandomUserAgent()),
            "Referer": referer
        }
        return headers

    def construct_requests(self, url, headers):
        response = requests.get(url=url, headers=headers)
        time.sleep(random.uniform(0, 1))
        return response

    def parse_html(self, html_str):
        html = etree.HTML(html_str)
        proxy = Proxy()
        tr_list = html.xpath('//tbody/tr')
        for tr in tr_list:
            ip = tr.xpath("./td[1]/text()")
            ip = ip[0] if ip else None
            port = tr.xpath('./td[2]/text()')
            port = port[0] if port else None
            area = tr.xpath('./td[5]/text()')
            area = area[0] if area else None
            proxy = Proxy(ip=ip, port=port, area=area)
            yield proxy

    def run(self):
        url_list = self.construct_url(self.first_url)
        for url in url_list:
            headers = self.construct_headers(url)
            response = self.construct_requests(url, headers)
            if response.ok:
                proxy_list = self.parse_html(html_str=response.content.decode('GBK'))
                yield from proxy_list


class Ip3366Spider(object):
    def __init__(self):
        self.first_url_list = [
            "http://www.ip3366.net/free/?stype=1",
            "http://www.ip3366.net/free/?stype=2",
        ]

    def get_proxies(self, first_url):
        proxies = Ip3366ProxySpider(first_url).run()
        yield from proxies

    def run(self):
        for first_url in self.first_url_list:
            try:
                proxies = self.get_proxies(first_url)
                yield from proxies
            except Exception as e:
                pass


if __name__ == "__main__":
    obj = Ip3366Spider()
    for ret in obj.run():
        print(ret)
