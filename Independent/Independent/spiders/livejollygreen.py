from Independent.spiders.base_spider import BaseSpider
import scrapy


class LiveJollyGreenSpider(BaseSpider):
    name = 'livejollygreen'
    allowed_domains = ['livejollygreen.com']
    start_urls = ['https://www.livejollygreen.com/service/']
    p_id = '990027'

    def parse(self, response):
        address = response.xpath('//form/div/div[2]/div[1]/p[1]/text()').get()
        postal_code = address.split(', ')[-1]
        city = 'Toronto'
        shop_name = 'Jolly Green Cannabis'
        img = 'https://cdn.shoplightspeed.com/shops/648438/themes/13296/v/271717/assets/logo.png?20210608165357'
        phone = response.xpath('//form/div/div[2]/div[1]/p[3]/text()').get()
        email = 'shop@livejollygreen.com'

        yield {
			"Producer ID": '',
			"p_id": self.p_id,
			"Producer": f"{shop_name}",
			"Description": '',
			"Link": 'https://www.livejollygreen.com',
			"SKU": "",
			"City": city,
			"Province": 'Ontario',
			"Store Name": shop_name,
			"Postal Code": postal_code,
			"long": '',
			"lat": '',
			"ccc": "",
			"Page Url": 'https://lovebud.shop',
			"Active": "",
			"Main image": img,
			"Image 2": "",
			"Image 3": "",
			"Image 4": '',
			"Image 5": '',
			"Type": "",
			"License Type": "",
			"Date Licensed": "",
			"Phone": phone,
			"Phone 2": "",
			"Contact Name": "",
			"EmailPrivate": "",
			"Email": email,
			"Social": "",
			"FullAddress": address,
			"Address": '',
			"Additional Info": "",
			"Created": '',
			"Comment": '',
			"Updated": ''
        }


        yield scrapy.Request('https://www.livejollygreen.com/collection/', callback=self.parse_products, dont_filter=True)

    def parse_products(self, response):
        for product in response.xpath('//div[@class="prod-card"]'):
            url = product.xpath('.//a/@href').get()
            yield scrapy.Request(url, callback=self.parse_product, dont_filter=True)

        if '/page' in response.xpath('//a[@class="pagination__item"]/@href').getall()[-1]:
            url = response.xpath('//a[@class="pagination__item"]/@href').getall()[-1]
            yield scrapy.Request(url, callback=self.parse_products, dont_filter=True)

    def parse_product(self, response):
        name = response.xpath('//div[contains(@class, "text-component")]/h1/text()').get().strip()
        sku = response.xpath('//div[contains(@class, "text-component")]/div/text()').get().replace('Article number: ', '').split('_')[0]
        weight = response.xpath('//div[contains(@class, "text-component")]/div/text()').get().replace('Article number: ', '').split('_')[1]
        attributes = response.xpath('//p[@class=""]/text()').getall()
        for item in attributes:
            if item.strip() == '':
                attributes.remove(item)
        thc = cbd = plant_type = weight = ''
        for item in attributes:
            if 'THC' in item and thc == '':
                thc = attributes[attributes.index(item)+1].strip()
            elif 'CBD' in item and cbd == '':
                cbd = attributes[attributes.index(item)+1].strip()
            elif 'PLANT TYPE' in item and plant_type == '':
                plant_type = attributes[attributes.index(item)+1].strip()
            elif 'SIZE' in item and weight == '':
                weight = attributes[attributes.index(item)+1].strip()
        desc = response.xpath('//section[@id="proTabPanelInformation"]/div/p/text()').get()
        try:
            desc = desc.replace('\n', '').replace('\r', '')
        except:
            pass
        image = response.xpath('//img[@class="img-mag__asset"]/@src').get()
        price = response.xpath('//div[contains(@class, "product__price text-md")]/text()').get().replace('C$', '')
        stock = response.xpath('//div[@class="in-stock"]/text()').getall()[-1].strip()
        if stock != 'In stock':
            stock = 'Out of Stock'
        

        yield {
            "Page URL": response.url,
            "Brand": '',
            "Name": name,
            "SKU": sku,
            "Out stock status": stock,
            "Stock count": '',
            "Currency": "CAD",
            "ccc": "",
            "Price": price,
            "Manufacturer": '',
            "Main image": image,
            "Description": desc,
            "Product ID": '',
            "Additional Information": '',
            "Meta description": "",
            "Meta title": "",
            "Old Price": '',
            "Equivalency Weights": '',
            "Quantity": '',
            "Weight": weight,
            "Option": "",
            "Option type": '',
            "Option Value": "",
            "Option image": "",
            "Option price prefix": "",
            "Cat tree 1 parent": '',
            "Cat tree 1 level 1": "",
            "Cat tree 1 level 2": "",
            "Cat tree 2 parent": '',
            "Cat tree 2 level 1": "",
            "Cat tree 2 level 2": "",
            "Cat tree 2 level 3": "",
            "Image 2": '',
            "Image 3": '',
            "Image 4": '',
            "Image 5": '',
            "Sort order": "",
            "Attribute 1": 'THC',
            "Attribute Value 1": thc,
            "Attribute 2": 'CBD',
            "Attribute value 2": cbd,
            "Attribute 3": 'Plant Type',
            "Attribute value 3": plant_type,
            "Attribute 4": '',
            "Attribute value 4": '',
            "Reviews": '',
            "Review link": '',
            "Rating": '',
            "Address": '',
            "p_id": self.p_id
        }