from LeaflyBased.spiders.keyword_spider import KeywordSpider


class LakeCityCannabisSpider(KeywordSpider):
    name = 'lake_city_cannabis'
    keyword = 'Lake City Cannabis'


if __name__ == '__main__':
    from scrapy.crawler import CrawlerProcess
    from scrapy.utils.project import get_project_settings

    process = CrawlerProcess(get_project_settings())
    process.crawl('lake_city_cannabis')
    process.start()
