from LeaflyBased.spiders.keyword_spider import KeywordSpider


class SpiritleafCanyonMeadowsSpider(KeywordSpider):
    name = 'spiritleaf_canyon_meadows'
    keyword = 'Spiritleaf - Canyon Meadows'


if __name__ == '__main__':
    from scrapy.crawler import CrawlerProcess
    from scrapy.utils.project import get_project_settings

    process = CrawlerProcess(get_project_settings())
    process.crawl('spiritleaf_canyon_meadows')
    process.start()
