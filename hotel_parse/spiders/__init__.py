import re
import json
import math
import scrapy
from urllib.parse import urljoin, urlparse, parse_qs
from hotel_parse.items import HotelItem


USER_AGENT = "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 " \
             "(KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36"
BLOCK_MSG = 'Too many requests received, ' \
            'please wait a few minutes and try again'
PAGE_LINK = 'https://www.tour.ne.jp/j_hotel/parts_hotel_list/?pg={}'
AGENT_LINK = 'https://www.tour.ne.jp/api/json/j_hotel/parts_plan_cond_data'
TOTAL_LINK = 'https://www.tour.ne.jp/api/json/j_hotel/parts_agent_cnt/'

HOTEL_HREF = '//*[starts-with(@id, "hotel_id")]/div[1]/div[2]/h2/a/@href'
NEXT_PAGE = '//*[@class="Act_pagination_next"]/@href'
TOTAL_PAGES = '//*[@id="lowerNavi"]/div[1]/span/b/text()'
NAME = '//*[@id="Area_hotel_name"]/text()'
PREFECTURE = '//*[@id="Area_detail_header"]/div[1]/div[2]/' \
             'ul[1]/li[1]/div[2]/a[1]/text()'
CITY = '//*[@id="Area_detail_header"]/div[1]/div[2]/ul[1]/' \
       'li[1]/div[2]/a[2]/text()'
ADDRESS = '//*[@id="Area_hotel_address"]/text()'
META_DATA = '/html/head/script/text()'
REVIEWS = '//*[@id="Area_detail_header"]/ul/li[2]/div[2]/span[2]/text()'
REVIEWS_URL = '//*[@id="Area_detail_header"]/ul/li[2]/div[2]/ul/li[3]/a/@href'
TO_OTHER_BOOKER_LINK = '//*[@id="main_Col"]/form/input[1]/@value'
OTHER_LINK = '//*[@id="sub_Col"]/div[1]/ul/li/a/@href'

HOTEL_TYPES_DICT = {
    1: 'ホテル',
    2: 'ペンション・民宿',
    3: '旅館',
    4: '貸別荘・コテージ',
    5: '民泊施設',
}


class TourHotelSpider(scrapy.Spider):
    name = "tour_hotel"
    start_urls = [AGENT_LINK]
    item_per_page = 25
    agent_dict = {}

    def start_requests(self):
        for url in self.start_urls:
            yield self.request(url, self.init)

    def init(self, response):
        if self.is_blocked(response):
            yield self.request(response, self.init)
        else:
            self.get_agent_description(response)
            yield self.request(TOTAL_LINK, self.parse_total)

    def parse_total(self, response):
        if self.is_blocked(response):
            yield self.request(response, self.init)
        else:
            total_pages = self.get_total_pages(response)
            for page_number in range(total_pages):
                page_url = PAGE_LINK.format(page_number + 1)
                yield self.request(page_url, self.parse_hotel_list)

    def parse_hotel_list(self, response):
        if self.is_blocked(response):
            yield self.request(response, self.parse_hotel_list)
        else:
            for hotel_link in response.xpath(HOTEL_HREF).extract():
                url = urljoin(response.url, hotel_link)
                yield self.request(url, self.parse_hotel)

    def parse_hotel(self, response):
        if self.is_blocked(response):
            yield self.request(response, self.parse_hotel)
        else:
            hotel_type, pos_x, pos_y = self.parse_meta(response)
            item = HotelItem()
            item['url'] = response.url
            item['name'] = self.parse_value(response, NAME)
            item['prefecture'] = self.parse_value(response, PREFECTURE)
            item['city'] = self.parse_value(response, CITY)
            item['address'] = self.parse_value(response, ADDRESS)
            item['rating'] = self.parse_value(response, REVIEWS)
            item['other_offers'] = self.parse_other_links(response)
            item['geo_coordinates'] = pos_x, pos_y
            item['type'] = hotel_type
            yield item

    def get_agent_description(self, response):
        agent_dict = json.loads(response.text)['response']['agt']
        self.agent_dict = {k: v['agent_name'] for k, v in agent_dict.items()}

    def get_total_pages(self, response):
        total = json.loads(response.text)['response']['totalCount']
        return int(math.ceil(int(total) / self.item_per_page))

    def parse_other_links(self, response):
        links = response.xpath(OTHER_LINK).extract()
        agents = []
        for link in links:
            agent_id = parse_qs(urlparse(link).query)['agent_id'][0]
            agents.append(self.agent_dict[agent_id])
        return agents

    def parse_hotel_reviews(self, response, item):
        # item['reviews_url'] = self.parse_value(response, REVIEWS_URL)
        # item['reviews_content_length'] = self.parse_value(response, REVIEWS_URL)
        # some logic that updates hotel reviews
        pass

    @staticmethod
    def request(url, callback):
        return scrapy.Request(url, callback)
    
    @staticmethod
    def is_blocked(response):
        return BLOCK_MSG in response.text

    @staticmethod
    def parse_value(response, path):
        value = response.xpath(path).extract()
        return value[0] if value else ''

    @staticmethod
    def parse_meta(response):
        hotel_type, pos_x, pos_y = [None] * 3
        try:
            for script in response.xpath(META_DATA).extract():
                if 'TRAVELKO.APP.hotel_type' in script:
                    values = script.split(';')
                    for value in values:
                        if hotel_type and pos_x and pos_y:
                            break
                        if value.startswith('TRAVELKO.APP.hotel_type'):
                            hotel_type = int(re.findall('"([^"]*)"', value)[0])
                        elif value.startswith('TRAVELKO.APP.pos_x'):
                            pos_x = re.findall('"([^"]*)"', value)[0]
                        elif value.startswith('TRAVELKO.APP.pos_y'):
                            pos_y = re.findall('"([^"]*)"', value)[0]
                    break
        except ValueError:
            pass
        if hotel_type:
            hotel_type = HOTEL_TYPES_DICT[hotel_type]
        return hotel_type, pos_x, pos_y
