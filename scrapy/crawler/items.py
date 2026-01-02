# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class entryText(scrapy.Item):
    entry_header = scrapy.Field()
    source_url = scrapy.Field()
    text_content = scrapy.Field()

class answerText(scrapy.Item):
    question = scrapy.Field()
    source_url = scrapy.Field()
    answer = scrapy.Field()
    