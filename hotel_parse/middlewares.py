import random
import logging

log = logging.getLogger('scrapy.proxies')


class RandomProxy(object):
    def __init__(self, settings):
        self.mode = settings.get('PROXY_MODE')
        self.proxy_list = settings.get('PROXY_LIST')

        if self.proxy_list is None:
            raise KeyError('PROXY_LIST setting is missing')
        self.proxies = set()
        fin = open(self.proxy_list)
        try:
            for line in fin.readlines():
                line = line.strip()
                if line:
                    self.proxies.add(line)
        finally:
            self.proxies.add('without')
            fin.close()

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def process_request(self, request, spider):
        if 'proxy' in request.meta:
            if request.meta["exception"] is False:
                return
        request.meta["exception"] = False
        if len(self.proxies) == 0:
            raise ValueError('All proxies are unusable, cannot proceed')
        proxy_address = random.choice(list(self.proxies))
        if proxy_address != 'without':
            request.meta['proxy'] = proxy_address
        log.debug('Using proxy <%s>, %d proxies left' % (
                proxy_address, len(self.proxies)))

    def process_response(self, request, response, spider):

        if response.status in [503]:
            logging.error(
                "%s found for %s so retrying" % (response.status, response.url))
            req = request.copy()
            req.dont_filter = True
            req.meta['proxy'] = random.choice(list(self.proxies))
            return req
        else:
            return response

    def process_exception(self, request, exception, spider):
        if 'proxy' not in request.meta:
            return
        proxy = request.meta['proxy']
        log.info(proxy)
        request.meta["exception"] = True
