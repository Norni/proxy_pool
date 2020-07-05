from proxy_pool.settings import DEFAULT_SCORE


class Proxy(object):

    def __init__(self, ip=None, port=None, protocol=None, nick_type=None, speed=None, score=DEFAULT_SCORE, area=None,
                 disable_domain=[]):
        self.ip = ip
        self.port = port
        self.protocol = protocol
        self.nick_type = nick_type
        self.speed = speed
        self.score = score
        self.area = area
        self.disable_domain = disable_domain

    def __str__(self):
        return str(self.__dict__)


if __name__ == "__main__":
    proxy = Proxy(ip='192.168.0.1', port='8885')
    print(proxy)
