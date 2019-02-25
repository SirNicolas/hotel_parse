import scrapy


class HotelItem(scrapy.Item):
    url = scrapy.Field()
    name = scrapy.Field()
    type = scrapy.Field()
    region = scrapy.Field()
    prefecture = scrapy.Field()
    city = scrapy.Field()
    address = scrapy.Field()
    geo_coordinates = scrapy.Field()
    rating = scrapy.Field()
    reviews_url = scrapy.Field()
    reviews_content_length = scrapy.Field()
    other_offers = scrapy.Field()
