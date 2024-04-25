import scrapy

from LeaflyBased.spiders.base_spider import BaseSpider


class BudaboomSpider(BaseSpider):
    name = 'budaboom'
    start_urls = ['https://www.budaboom.com/']
    custom_settings = {'COOKIES_ENABLED': True}

    def parse(self, response, **kwargs):
        form = response.xpath('//div[@class="age-gate"]/form')
        url = form.xpath('@action').extract_first()

        formdata = {'age_gate[confirm]': '1'}
        inputs = form.xpath('input')
        for one in inputs:
            formdata[one.xpath('@name').extract_first()] = one.xpath('@value').extract_first()

        yield scrapy.FormRequest(url,
                                 formdata=formdata,
                                 callback=self.parse_shops)

    def parse_shops(self, response):
        shops = response.xpath('//ul[@id="menu-menu-1"]/li/a[contains(text(), "Shop")]/@href').extract()
        for url in shops:
            yield scrapy.Request(url,
                                 callback=self.parse_shops)

        shop_id = response.xpath('//script[@id="leafly-embed-script"]/@data-slug').extract_first()
        if not shop_id:
            return

        link = f'https://consumer-api.leafly.com/api/dispensaries/v2/{shop_id}/menu_items?take=18&skip=0&'
        yield scrapy.Request(link,
                             headers=self.headers,
                             callback=self.parse_menu)


if __name__ == '__main__':
    from scrapy.crawler import CrawlerProcess
    from scrapy.utils.project import get_project_settings

    process = CrawlerProcess(get_project_settings())
    process.crawl('budaboom')
    process.start()
