from urllib.parse import urljoin

import scrapy

from LeaflyBased.spiders.base_spider import BaseSpider


class PrestigegreenSpider(BaseSpider):
    name = 'prestigegreen'
    start_urls = ['https://www.prestigegreen.com/']
    custom_settings = {'COOKIES_ENABLED': True}

    def parse(self, response, **kwargs):
        form_data = {'age_gate[confirm]': "1"}
        form = response.xpath('//form[@class="age-gate-form"]')
        url = form.xpath('@action').extract_first()
        inputs = form.xpath('input')
        for one in inputs:
            name = one.xpath('@name').extract_first()
            value = one.xpath('@value').extract_first()
            form_data[name] = value

        yield scrapy.FormRequest(url,
                                 formdata=form_data,
                                 callback=self.parse_age)

    def parse_age(self, response):
        links = response.xpath('//ul[@class="menu"]/li/a[contains(@href, "menu")]/@href').extract()
        for link in links:
            yield scrapy.Request(link,
                                 callback=self.parse_entry)

    def parse_entry(self, response):
        wrapper = response.xpath('//script[@id="leafly-embed-script"]')
        if not wrapper:
            return

        # data_origin = wrapper.xpath('@data-origin').extract_first()
        data_slug = wrapper.xpath('@data-slug').extract_first()
        link = f'https://www.leafly.com/dispensary-info/{data_slug}/menu'
        if not link or 'leafly.com' not in link:
            return

        yield scrapy.Request(link,
                             callback=self.parse_menu,
                             meta={'dont_merge_cookies': True})


if __name__ == '__main__':
    from scrapy.crawler import CrawlerProcess
    from scrapy.utils.project import get_project_settings

    process = CrawlerProcess(get_project_settings())
    process.crawl('prestigegreen')
    process.start()
