import scrapy

from LeaflyBased.spiders.base_spider import BaseSpider


class A6ofspadeSpider(BaseSpider):
    name = '6ofspade'
    start_urls = ['https://6ofspade.com/collections/']
    custom_settings = {'PROXY_URL': 'http://127.0.0.1:24002'}

    def parse(self, response, **kwargs):
        data_slug = response.xpath('//script[@id="leafly-embed-script"]/@data-slug').extract_first()
        url = f'https://consumer-api.leafly.com/api/dispensaries/v2/{data_slug}/menu_items'
        yield scrapy.Request(url,
                             headers={'Accept': 'application/json',
                                      'Referer': 'https://web-embedded-menu.leafly.com/',
                                      'X-App': 'web-embedded-menu',
                                      'X-Environment': 'production'},
                             callback=self.parse_menu)


if __name__ == '__main__':
    from scrapy.crawler import CrawlerProcess
    from scrapy.utils.project import get_project_settings

    process = CrawlerProcess(get_project_settings())
    process.crawl('6ofspade')
    process.start()
