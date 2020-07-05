from proxy_pool.settings import USER_AGENTS
import random


class RandomUserAgent(object):
    def __init__(self):
        self.user_agents = USER_AGENTS

    def __str__(self):
        return random.choice(self.user_agents)


if __name__ == "__main__":
    obj = RandomUserAgent()
    print(obj)
