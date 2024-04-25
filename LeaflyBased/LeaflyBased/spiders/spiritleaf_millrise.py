from LeaflyBased.spiders.keyword_spider import KeywordSpider


class SpiritleafMillriseSpider(KeywordSpider):
    name = 'spiritleaf_millrise'
    keyword = 'Spiritleaf - Millrise'


if __name__ == '__main__':
    from scrapy.crawler import CrawlerProcess
    from scrapy.utils.project import get_project_settings

    process = CrawlerProcess(get_project_settings())
    process.crawl('spiritleaf_millrise')
    process.start()
