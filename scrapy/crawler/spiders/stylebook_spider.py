
import scrapy
import re
from scrapy.http import FormRequest
from scrapy.linkextractors import LinkExtractor
from crawler.items import entryText


class stylebookSpider(scrapy.Spider):
    name = "stylebook"
    login_url = "https://www.apstylebook.com/users/sign_in"

    link_extractor = LinkExtractor(
            allow= [
                '/ap_stylebook',
                ],
            allow_domains=["apstylebook.com"]
            )
    
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
            callback=self.parse,
            )

    def is_stylebook_url(self, url):
        stylebook_re = re.compile(r"^https?://(www\.)?apstylebook\.com/ap_stylebook/[^/?#]+/?$")

        if stylebook_re.match(url):
            return True
    
    def parse(self, response):
        if self.is_stylebook_url(response.url):
            self.logger.info(f"Scraping article: {response.url}")

            scraped_text = entryText()

            header = response.xpath("//h1[@class='entry_header']/text()").get()
            entry = response.xpath("//div[@class='entry_content']//text()").getall()

            scraped_text['source_url'] = response.url
            scraped_text['entry_header'] = header.strip() 
            scraped_text['text_content'] = " ".join(t.strip() for t in entry if t.strip())

            yield scraped_text
            return
        
        links = self.link_extractor.extract_links(response)
        self.logger.info(f"Extracted {len(links)} links from {response.url}")

        for link in links:
            yield response.follow(link.url, callback=self.parse)

        next_page = response.css("a.next::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
