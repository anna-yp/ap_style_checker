from pathlib import Path

import scrapy
from scrapy.http import FormRequest


class ExampleSpider(scrapy.Spider):
    name = "quotes"
    login_url = "https://www.apstylebook.com/users/sign_in"
    start_urls = [
        "https://www.apstylebook.com/ap_stylebook",
    ]
    
    async def start(self):
        yield scrapy.Request(
            url=self.login_url,
            callback=self.login,
        )
    

    def login(self, response):
        csrf = response.xpath("//meta[@name='csrf-token']/@content").extract_first()

        yield FormRequest(
            url=self.login_url,
            formdata={
                "authenticity_token": csrf,
                'user[login]': 'scotscoopeditor2@gmail.com',
                'user[password]': '',
            },
            callback=self.after_login,
            )
        
    def after_login(self, response):

        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.parse)

    def parse(self, response):
        page = response.url.split("/")[-2]
        filename = f"{page}.html"
        Path(filename).write_bytes(response.body)