# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class Text(scrapy.Item):
    category = scrapy.Field()
    source_url = scrapy.Field()
    text_content = scrapy.Field()
    
