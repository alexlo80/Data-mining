import os
import dotenv
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from gb_parse.spiders.autoyoula import AutoyoulaSpider
from gb_parse.spiders.instagram import InstagramSpider


if __name__ == "__main__":
    crawler_settings = Settings()
    crawler_settings.setmodule("gb_parse.settings")
    crawler_proc = CrawlerProcess(settings=crawler_settings)
    dotenv.load_dotenv(".env")
    insta_tags = ["python", "programming"]
    insta_params = {
        "username": os.getenv("USERNAME"),
        "enc_password": os.getenv("ENC_PASSWORD"),
        "tags": insta_tags,
    }
    crawler_proc.crawl(InstagramSpider, **insta_params)
    crawler_proc.start()