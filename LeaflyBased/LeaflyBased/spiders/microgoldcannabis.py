import scrapy

from LeaflyBased.spiders.base_spider import BaseSpider


class MicrogoldcannabisSpider(BaseSpider):
    name = 'microgoldcannabis'
    start_urls = ['https://www.microgoldcannabis.com/']

    def parse(self, response, **kwargs):
        span = response.xpath('//a/span[contains(concat(" ", normalize-space(text()), " "), "Order Online")]')
        if not span:
            return
        link = span.xpath('../@href').extract_first()
        if not link or 'leafly.com' not in link:
            return

        if not link.endswith('/menu'):
            link = f'{link}/menu'
        yield scrapy.Request(link,
                             callback=self.parse_menu)


if __name__ == '__main__':
    from scrapy.crawler import CrawlerProcess
    from scrapy.utils.project import get_project_settings

    process = CrawlerProcess(get_project_settings())
    process.crawl('microgoldcannabis')
    process.start()
