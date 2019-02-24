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
    reviews = scrapy.Field()
    other_offers = scrapy.Field()
