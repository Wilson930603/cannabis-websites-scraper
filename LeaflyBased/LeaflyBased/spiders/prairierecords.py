import scrapy

from LeaflyBased.spiders.base_spider import BaseSpider


class PrairierecordsSpider(BaseSpider):
    name = 'prairierecords'
    start_urls = ['https://www.prairierecords.ca/pages/store-menus']

    def parse(self, response, **kwargs):
        links = response.xpath('//div[@class="rte"]/p/a[contains(@href, "leafly.com")]/@href').extract()
        for link in links:
            if not link.endswith('/menu'):
                link = f'{link}/menu'
            yield scrapy.Request(link,
                                 callback=self.parse_menu)


if __name__ == '__main__':
    from scrapy.crawler import CrawlerProcess
    from scrapy.utils.project import get_project_settings

    process = CrawlerProcess(get_project_settings())
    process.crawl('prairierecords')
    process.start()
