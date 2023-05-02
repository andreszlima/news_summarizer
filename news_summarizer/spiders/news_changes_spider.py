import scrapy
from bs4 import BeautifulSoup
from sumy.parsers.html import HtmlParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer
from news_summarizer.items import NewsItem

class NewsChangesSpider(scrapy.Spider):
    name = "news_changes"
    start_urls = ["https://www.uol.com.br/"]

    def parse(self, response):
        soup = BeautifulSoup(response.text, "html.parser")
        news_titles = soup.select(".hyperlink.headlineMain__link")
        for news_title in news_titles:
            link = news_title.get("href")
            title = news_title.get_text(strip=True)
            yield scrapy.Request(link, callback=self.parse_article, meta={"title": title, "link": link})

    def parse_article(self, response):
        title = response.meta["title"]
        link = response.meta["link"]
        soup = BeautifulSoup(response.text, "html.parser")
        body = soup.select_one(".c-news__body")
        body_text = body.get_text(strip=True)
        parser = HtmlParser.from_string(str(body), response.url, Tokenizer("portuguese"))
        summarizer = LexRankSummarizer()
        summary = summarizer(parser.document, sentences_count=6)
        summary_text = "\n".join(str(s) for s in summary)
        item = NewsItem(title=title, link=link, summary=summary_text, body=body_text)
        yield item