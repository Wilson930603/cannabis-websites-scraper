import json

import scrapy

from LeaflyBased.spiders.base_spider import BaseSpider


class OntarioSpider(BaseSpider):
    name = 'ontario'
    start_urls = ['https://www.leafly.ca/dispensaries/ontario?filter=pickup']

    def parse(self, response, **kwargs):
        json_data = response.xpath('//script[@id="__NEXT_DATA__"]/text()').extract_first()
        json_data = json.loads(json_data)
        center = json_data['props']['pageProps']['contextData']['mapContext']['center']
        config_context = json_data['props']['pageProps']['contextData']['configContext']
        yield scrapy.Request(f'https://web-finder.leafly.com/api/get-dispensaries'
                             f'?userLat={center["lat"]}&userLon={center["lng"]}'
                             f'&countryCode={config_context["countryCode"]}'
                             f'&retailType={config_context["retailType"]}'
                             f'&sort=default&geoQueryType=point&radius=680.6456184973142mi'
                             f'&filters[]=pickup&page=1&limit=10000&useV3EndpointEnabled=true&newDefaultSort=default',
                             headers=self.headers,
                             callback=self.parse_query)

    def parse_query(self, response):
        result = json.loads(response.text)
        for one in result['stores']:
            url = f'https://www.leafly.com/dispensary-info/{one["slug"]}/menu'
            yield scrapy.Request(url,
                                 callback=self.parse_menu)


if __name__ == '__main__':
    from scrapy.crawler import CrawlerProcess
    from scrapy.utils.project import get_project_settings

    process = CrawlerProcess(get_project_settings())
    process.crawl('ontario')
    process.start()
