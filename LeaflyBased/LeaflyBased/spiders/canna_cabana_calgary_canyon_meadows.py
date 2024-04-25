from LeaflyBased.spiders.keyword_spider import KeywordSpider


class CannaCabanaCalgaryCanyonMeadowsSpider(KeywordSpider):
    name = 'canna_cabana_calgary_canyon_meadows'
    keyword = 'Canna Cabana - Calgary - Canyon Meadows'


if __name__ == '__main__':
    from scrapy.crawler import CrawlerProcess
    from scrapy.utils.project import get_project_settings

    process = CrawlerProcess(get_project_settings())
    process.crawl('canna_cabana_calgary_canyon_meadows')
    process.start()
