import scrapy

from LeaflyBased.spiders.base_spider import BaseSpider


class LakewoodcannabisSpider(BaseSpider):
    name = 'lakewoodcannabis'
    start_urls = ['http://lakewoodcannabis.ca//shop']

    def parse(self, response, **kwargs):
        link = response.xpath('//a[contains(@href, "leafly.com")]/@href').extract_first()
        if not link:
            return

        if not link.endswith('/menu'):
            link = f'{link}/menu'
        yield scrapy.Request(link,
                             callback=self.parse_menu)


if __name__ == '__main__':
    from scrapy.crawler import CrawlerProcess
    from scrapy.utils.project import get_project_settings

    process = CrawlerProcess(get_project_settings())
    process.crawl('lakewoodcannabis')
    process.start()
