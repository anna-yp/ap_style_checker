
import scrapy
from crawler.items import answerText
from scrapy_playwright.page import PageMethod


class stylebookSpider(scrapy.Spider):
    name = "editors"
    login_url = "https://www.apstylebook.com/users/sign_in"

    custom_settings = {
        "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
        "DOWNLOAD_HANDLERS": {
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        },
        "LOG_LEVEL": "DEBUG",
    }

    def start_requests(self):
        print('hit start')
        yield scrapy.Request(
            url="https://www.apstylebook.com/users/sign_in",
            meta={
                "playwright": True,
                "playwright_page_methods": [
                    PageMethod("wait_for_load_state", "networkidle"),
                    PageMethod("fill", "input[name='user[login]']", 'scotscoopeditor3@gmail.com'),
                    PageMethod("fill", "input[name='user[password]']", '$c0tSc00p'),
                    PageMethod("click", "input[name='commit']"),
                ],
            },
            callback=self.after_login,
            )
        
    def after_login(self, response):
        print("Made it to after log in")
        yield scrapy.Request(
            url="https://www.apstylebook.com/ask_the_editors",
            meta={
                "playwright": True,
                "playwright_page_methods": [
                    PageMethod(
                        "evaluate",
                        """
                        (async () => {
                            let lastHref = null;
                            while (true) {
                                const button = document.querySelector("a.recent-load-more.d-block.py-1.px-2");
                                if (!button || button.offsetParent === null) break;

                                const prevCount = document.querySelectorAll("#recent_entries div.question.p-2").length;

                                button.click();

                                let attempts = 0;
                                while (
                                    document.querySelectorAll("#recent_entries div.question.p-2").length <= prevCount && attempts < 10
                                ) {
                                    await new Promise(r => setTimeout(r, 500));
                                    attempts++;
                                }

                                const entries = document.querySelectorAll("#recent_entries div.question.p-2 a");

                                const lastLink = entries[entries.length - 1];
                                const href = lastLink?.getAttribute("href");
                                
                                if (!href || href === lastHref) break;
                                lastHref = href;
                            }
                        })();
                        """
                    ),
                ]
            },
            callback=self.parse
        )

    def parse(self, response, **kwargs):
        count = len(response.css("div.question.p-2"))

        for i in range(count):
            scraped_text = answerText()

            question = response.css("div.question.p-2")[i].css("::text").getall()
            question_filtered = [
                string.strip()
                for string in question
                    if (stripped_string := string.strip()) and stripped_string not in {"Question", "Answer"}
                ]
            question_text = " ".join(question_filtered)

            answer = response.css("div.answer.p-2")[i].css("::text").getall()
            answer_filtered = [
                string.strip()
                for string in answer
                    if (stripped_string := string.strip()) and stripped_string not in {"Question", "Answer"}
                ]
            answer_text = " ".join(answer_filtered)

            source = response.css("div.question.p-2")[i].css("::attr(href)").get()

            scraped_text['source_url'] = f'apstylebook.com{source}'
            scraped_text['question'] = question_text
            scraped_text['answer'] = answer_text

            yield scraped_text

        print({"url": response.url, "count": len(response.css("#recent_entries div.question.p-2").getall())})
