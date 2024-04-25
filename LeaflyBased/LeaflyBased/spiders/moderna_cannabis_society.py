from LeaflyBased.spiders.keyword_spider import KeywordSpider


class ModernaCannabisSocietySpider(KeywordSpider):
    name = 'moderna_cannabis_society'
    keyword = 'Moderna Cannabis Society'


if __name__ == '__main__':
    from scrapy.crawler import CrawlerProcess
    from scrapy.utils.project import get_project_settings

    process = CrawlerProcess(get_project_settings())
    process.crawl('moderna_cannabis_society')
    process.start()
