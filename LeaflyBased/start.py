from scrapy.utils.project import get_project_settings
from scrapy.crawler import CrawlerProcess


if __name__ == '__main__':
    setting = get_project_settings()
    process = CrawlerProcess(setting)

    for spider_name in process.spiders.list():
        print(f"Running spider {spider_name}")
        process.crawl(spider_name)

    process.start()
