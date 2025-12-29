from pathlib import Path

import scrapy
from scrapy.http import FormRequest


class ExampleSpider(scrapy.Spider):
    name = "quotes"
    start_urls = [
        "https://www.apstylebook.com/",
    ]
    
    def start_requests(self):
        login_url = 'http://quotes.toscrape.com/login'
        return scrapy.Request(login_url, callback=self.login)
    
    def login(self, response):
        token = response.css("form input[name=csrf_token]::attr(value)").extract_first()
        return FormRequest.from_response(response,
                                         formdata={'csrf_token': token,
                                                   'password': 'foobar',
                                                   'username': 'foobar'},
                                         callback=self.start_scraping)

    def parse(self, response):
        page = response.url.split("/")[-2]
        filename = f"quotes-{page}.html"
        Path(filename).write_bytes(response.body)