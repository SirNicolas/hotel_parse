from pathlib import Path

CONCURRENT_ITEMS = 20

RETRY_TIMES = 5
RETRY_HTTP_CODES = [500, 504, 400, 403, 404, 408]
DOWNLOAD_TIMEOUT = 10

PROXY_LIST = str(Path(__file__).parent.parent) + '/list.txt'

BOT_NAME = 'hotel_parse'

SPIDER_MODULES = ['hotel_parse.spiders']
NEWSPIDER_MODULE = 'hotel_parse.spiders'

MONGODB_SERVER = "localhost"
MONGODB_PORT = 27017
MONGODB_DB = "hotel"
MONGODB_COLLECTION = "hotels"

SPIDER_MIDDLEWARES = {
}

DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': 90,
    'hotel_parse.middlewares.RandomProxy': 100,
    'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
}

ITEM_PIPELINES = {
   'hotel_parse.pipelines.HotelParsePipeline': 300,
}
