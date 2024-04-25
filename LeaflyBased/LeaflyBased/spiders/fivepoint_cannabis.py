from LeaflyBased.spiders.keyword_spider import KeywordSpider


class FivePointCannabisSpider(KeywordSpider):
    name = 'fivepoint_cannabis'
    keyword = 'FivePoint Cannabis'


if __name__ == '__main__':
    from scrapy.crawler import CrawlerProcess
    from scrapy.utils.project import get_project_settings

    process = CrawlerProcess(get_project_settings())
    process.crawl('fivepoint_cannabis')
    process.start()
