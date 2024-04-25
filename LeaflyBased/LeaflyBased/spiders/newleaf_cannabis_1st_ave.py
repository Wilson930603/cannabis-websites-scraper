from LeaflyBased.spiders.keyword_spider import KeywordSpider


class NewLeafCannabis1stAveSpider(KeywordSpider):
    name = 'newleaf_cannabis_1st_ave'
    keyword = 'NewLeaf Cannabis - 1st Ave'


if __name__ == '__main__':
    from scrapy.crawler import CrawlerProcess
    from scrapy.utils.project import get_project_settings

    process = CrawlerProcess(get_project_settings())
    process.crawl('newleaf_cannabis_1st_ave')
    process.start()
