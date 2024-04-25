from urllib.parse import urljoin

import scrapy

from Independent.spiders.base_spider import BaseSpider


class GanjahutyegSpider(BaseSpider):
    name = 'ganjahut'
    allowed_domains = ['ganjahutyeg.com']
    start_urls = ['https://ganjahutyeg.com/Products']

    # def start_requests(self):
    #     yield scrapy.Request('https://ganjahutyeg.com/product/dried-flower-sour-kush',
    #                          callback=self.parse_details)

    def parse(self, response, **kwargs):
        links = response.xpath('//div[@class="single-product mb-60"]'
                               '/div[@class="product-img"]/a/@href').extract()
        for link in links:
            url = urljoin(self.start_urls[0], link)
            yield scrapy.Request(url,
                                 callback=self.parse_details)

        next_page = response.xpath('//span[@id="BodyContentPlaceHolder_BottomDataPager"]'
                                   '/a[contains(text(), "Next")]/@href').extract_first()
        if next_page:
            next_page = next_page.replace("javascript:__doPostBack('", "").replace("','')", "")
            arguments = ['__EVENTARGUMENT',
                         '__LASTFOCUS',
                         '__VIEWSTATE',
                         '__VIEWSTATEGENERATOR',
                         '__EVENTVALIDATION']
            data = {
                'ctl00$BodyContentPlaceHolder$MainScriptManager':
                    f'ctl00$BodyContentPlaceHolder$MainUpdatePanel|{next_page}',
                '__EVENTTARGET': next_page,
                "ctl00$BodyContentPlaceHolder$SearchTextBox": "",
                "ctl00$BodyContentPlaceHolder$CategoriesRadioButtonList": "1",
                "__ASYNCPOST": "true",
                "": ""
            }
            if '</html' in response.text:
                for one in arguments:
                    data[one] = response.xpath(f'//input[@id="{one}"]/@value').extract_first()
            else:
                content = response.text.split('</section>')[-1]
                content = content.split('|')
                for one in arguments:
                    index = content.index(one)
                    if index < 0:
                        continue
                    data[one] = content[index + 1]
            headers = {'X-MicrosoftAjax': "Delta=true",
                       "X-Requested-With": "XMLHttpRequest",
                       "Accept": "*/*",
                       "Alt-Used": "ganjahutyeg.com",
                       "Content-Type": "application/x-www-form-urlencoded; charset=utf-8"}
            yield scrapy.FormRequest(self.start_urls[0],
                                     headers=headers,
                                     formdata=data,
                                     callback=self.parse)

        if 'class="footer-widget-section mb-30"' in response.text:
            description = response.xpath('//div[@class="footer-widget mb-50"]'
                                         '/p[@class="mb-30"]/text()').extract_first()
            logo = response.xpath('//div[@class="footer-widget mb-50"]'
                                  '/a[@class="logo d-block mb-35"]/img/@src').extract_first()
            if logo:
                logo = urljoin(self.start_urls[0], logo)
            phone = response.xpath('//div[@class="phone-number text-white"]/h5/text()').extract_first()
            address_i = response.xpath('//p/i[@class="far fa-map-marker-alt"]')
            address = address_i.xpath('../text()').extract_first()

            item = {"Producer ID": '',
                    "p_id": 'ganjahutyeg.com',
                    "Producer": 'Ganja Hut - Edmonton',
                    "Description": description.strip() if description else '',
                    "Link": 'https://ganjahutyeg.com',
                    "SKU": "",
                    "City": 'Edmonton',
                    "Province": 'AB',
                    "Store Name": 'Ganja Hut',
                    "Postal Code": 'T6B 2W8',
                    "long": '-113.4177561',
                    "lat": '53.5111352',
                    "ccc": "",
                    "Page Url": "",
                    "Active": "",
                    "Main image": logo,
                    "Image 2": '',
                    "Image 3": '',
                    "Image 4": '',
                    "Image 5": '',
                    "Type": "",
                    "License Type": "",
                    "Date Licensed": "",
                    "Phone": phone,
                    "Phone 2": "",
                    "Contact Name": "",
                    "EmailPrivate": "",
                    "Email": 'info@ganjahutyeg.com',
                    "Social": {'Facebook': 'https://www.facebook.com/ganjahutyeg',
                               'Instagram': 'https://instagram.com/ganjahutyeg'},
                    "FullAddress": address,
                    "Address": address,
                    "Additional Info": "",
                    "Created": "",
                    "Comment": "",
                    "Updated": ""}
            yield item

    def parse_details(self, response):
        name = response.xpath('//div[@class="product-desc"]/h3/text()').extract_first()
        categories = response.xpath('//div[@class="page-menu"]/nav/ul'
                                    '/li[contains(@class, "page-item")]/a/text()').extract()
        categories = [x.strip() for x in categories if x.strip()]

        properties = {}
        containers = response.xpath('//div[@class="product-desc"]'
                                    '/div[@class="row"]/div/div[@class="event-title"]')
        for one in containers:
            key = one.xpath('p[@class="mb-1"]/a/text()').extract_first()
            value = one.xpath('h6[@class="mb-20"]/text()').extract_first()
            properties[key] = value

        sold_out_button = response.xpath('//div[contains(@class, "sidebar-box")]'
                                         '/button[contains(text(), "SOLD")]')
        class_name = sold_out_button.xpath('../@class').extract_first()
        sold_out = False if 'd-none' in class_name else True

        images = response.xpath('//a[contains(@class, "nav-link") and not (contains(@class, "d-none"))]'
                                '/img/@src').extract()
        image_count = len(images)

        description = response.xpath('//div[@id="pills-home"]/p/text()').extract()
        description = '\n'.join(description)

        option_title = response.xpath('//div[@class="sidebar-box mb-4 p-0 "]'
                                      '/p[@class="mb-1 ml-1"]/text()').extract_first()
        item = {"Page URL": response.url,
                "Brand": properties.get('BRAND'),
                "Name": name,
                "SKU": name,
                "Out stock status": 'SOLD OUT' if sold_out else 'IN STOCK',
                "Stock count": 0 if sold_out else 1,
                "Currency": "CAD",
                "ccc": "",
                "Price": '0.01',
                "Manufacturer": properties.get('SUPPLIER'),
                "Main image": images[0] if image_count > 0 else '',
                "Description": description,
                "Product ID": '',
                "Additional Information": '',
                "Meta description": "",
                "Meta title": "",
                "Old Price": '0.01',
                "Equivalency Weights": "",
                "Quantity": '',
                "Weight": '',
                "Option": option_title,
                "Option type": 'Select',
                "Option Value": '',
                "Option image": "",
                "Option price prefix": '',
                "Cat tree 1 parent": categories[0],
                "Cat tree 1 level 1": categories[1],
                "Cat tree 1 level 2": "",
                "Cat tree 2 parent": "",
                "Cat tree 2 level 1": "",
                "Cat tree 2 level 2": "",
                "Cat tree 2 level 3": "",
                "Image 2": images[1] if image_count > 1 else '',
                "Image 3": images[2] if image_count > 2 else '',
                "Image 4": images[3] if image_count > 3 else '',
                "Image 5": images[4] if image_count > 4 else '',
                "Sort order": "",
                "Attribute 1": "CBD",
                "Attribute Value 1": properties.get('CBD'),
                "Attribute 2": "THC",
                "Attribute value 2": properties.get('THC'),
                "Attribute 3": "STRAIN NAME",
                "Attribute value 3": properties.get('STRAIN NAME'),
                "Attribute 4": "",
                "Attribute value 4": '',
                "Reviews": '',
                "Review link": "",
                "Rating": '',
                "Address": '',
                "p_id": 'ganjahutyeg.com'}

        variants = response.xpath('//select[@id="BodyContentPlaceHolder_PackagesDropDownList"]'
                                  '/option/text()').extract()
        if variants:
            for sku in variants:
                item["SKU"] = sku
                item["Option Value"] = sku
                yield item
        else:
            yield item


if __name__ == '__main__':
    from scrapy.crawler import CrawlerProcess
    from scrapy.utils.project import get_project_settings

    process = CrawlerProcess(get_project_settings())
    process.crawl('ganjahut')
    process.start()
