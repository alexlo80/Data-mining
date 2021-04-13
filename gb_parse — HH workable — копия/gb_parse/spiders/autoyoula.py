import re

import pymongo
import scrapy
from urllib.parse import urljoin

from gb_parse.loaders import HHLoader


class HhSpider(scrapy.Spider):
    name = "hh"
    allowed_domains = ["hh.ru"]
    start_urls = [
        "https://spb.hh.ru/search/vacancy?schedule=remote&L_profession_id=0&area=113"
    ]

    _xpath_data_query = {
        "title": '//h1[@data-qa="vacancy-title"]/text()',
        "salary": '//p[@class="vacancy-salary"]/span/text()',
        "description": '//div[@data-qa="vacancy-description"]//text()',
        "skills": '//div[@class="bloko-tag-list"]//'
        'div[contains(@data-qa, "skills-element")]/'
        'span[@data-qa="bloko-tag__text"]/text()',
        "author": '//a[@data-qa="vacancy-company-employer"]/@href',
        # "author": '//a[@data-qa="vacancy-company-name"]/@href',
    }

    _xpaths_selectors = {
        "pagination": '//div[@data-qa="pager-block"]//a[@data-qa="pager-page"]/@href',
        "vacancy": '//div[contains(@data-qa, "vacancy-serp__vacancy")]//'
        'a[@data-qa="vacancy-serp__vacancy-title"]/@href',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db_client = pymongo.MongoClient()

    def _get_follow_xpath(self, response, xpath, callback):
        for url in response.xpath(xpath):
            yield response.follow(url, callback=callback)

    def parse(self, response, *args, **kwargs):
        yield from self._get_follow_xpath(
            response, self._xpaths_selectors["brands"], self.brand_parse
        )

    def parse(self, response, **kwargs):
        yield from self._get_follow_xpath(
            response, self._xpaths_selectors["pagination"], self.parse,
        )
        yield from self._get_follow_xpath(
            response, self._xpaths_selectors["vacancy"], self.vacancy_parse,
        )
    def vacancy_parse(self, response):
        loader = HHLoader(response=response)
        loader.add_value("url", response.url)
        for key, xpath in self._xpath_data_query.items():
            loader.add_xpath(key, xpath)
        yield loader.load_item()

    def company_parse(self,response,):