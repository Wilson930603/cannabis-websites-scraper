from Independent.spiders.base_spider import BaseSpider
import scrapy


class PiffingtonsSpider(BaseSpider):
    name = 'piffingtons'
    allowed_domains = ['piffingtons.com']
    start_urls = ['http://www.piffingtons.com/contact/']
    p_id = '990042'
    shop_name = 'Piffingtons'

    def parse(self, response):
        description = response.xpath('//div[contains(@class, "elementor-element-d8868ab")]/div/p/text()').get()
        address = response.xpath('//div[contains(@class, "elementor-element-407b38e")]/div/div[1]/div/p/text()').get()
        phone = response.xpath('//div[contains(@class, "elementor-element-043a9ed")]/div/div[1]/div/p/text()').get()
        logo = response.xpath('//img[@alt="Piffingtons"]/@src').get()
        email = response.xpath('//div[contains(@class, "elementor-element-5cda607")]/div/div[1]/div/p/text()').get()

        yield {
			"Producer ID": '',
			"p_id": self.p_id,
			"Producer": f"{self.shop_name}",
			"Description": description,
			"Link": 'http://www.piffingtons.com',
			"SKU": "",
			"City": address.split(',')[0],
			"Province": 'Ontario',
			"Store Name": self.shop_name,
			"Postal Code": '',
			"long": '',
			"lat": '',
			"ccc": "",
			"Page Url": 'http://www.piffingtons.com/',
			"Active": "",
			"Main image": logo,
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
			"Created": "",
			"Comment": "",
			"Updated": ""
        }

        yield scrapy.Request('https://www.piffingtons.com/shop/page/1', callback=self.parse_products, dont_filter=True)

    n = 1
    def parse_products(self, response):
        links = response.xpath('//a[@class="woocommerce-LoopProduct-link"]/@href').getall()
        for link in links:
            print(link)
            yield scrapy.Request(link, callback=self.parse_product, dont_filter=True)
        if links:
            self.n += 1
            yield scrapy.Request('https://www.piffingtons.com/shop/page/'+str(self.n), callback=self.parse_products, dont_filter=True)

    
    def parse_product(self, response):
        name = response.xpath('//h1/text()').get()
        sku = response.xpath('//span[@class="sku"]/text()').get()
        price = response.xpath('//div[@class="price-single"]/div/span/text()').get()
        oldPrice = response.xpath('//div[@class="price-single"]/div/del/span/text()').get()
        qty = response.xpath('//input[contains(@class, "qty")]/@max').get()
        productID = response.xpath('//input[@type="hidden"]/@value').get()
        stock = 'In Stock'
        img_url = response.xpath('//img[@id="image"]/@src').get()
        description = response.xpath('//div[@class="description"]/p/text()').get()
        description = description.replace('\n', ' ') if description else ''
        categories = response.xpath('//span[@class="posted_in"]/a/text()').getall()
        reviews = response.xpath('//a[@href="#tab-reviews"]/text()').get().split('(')[-1].split(')')[0]
        images = response.xpath('//img[@class="attachment-shop_catalog size-shop_catalog"]/@src').getall()

        yield {
				"Page URL": response.url,
				"Brand": '',
				"Name": name,
				"SKU": sku,
				"Out stock status": stock,
				"Stock count": qty,
				"Currency": "CAD",
				"ccc": "",
				"Price": price,
				"Manufacturer": '',
				"Main image": img_url,
				"Description": description,
				"Product ID": productID,
				"Additional Information": '',
				"Meta description": "",
				"Meta title": "",
                
				"Old Price": oldPrice,
				"Equivalency Weights": '',
				"Quantity": '',
				"Weight": '',
				"Option": "",
				"Option type": '',
				"Option Value": "",
				"Option image": "",
				"Option price prefix": "",
				"Cat tree 1 parent": categories[0] if len(categories) > 0 else '',
				"Cat tree 1 level 1": '',
				"Cat tree 1 level 2": "",
				"Cat tree 2 parent": categories[1] if len(categories) > 1 else '',
				"Cat tree 2 level 1": "",
				"Cat tree 2 level 2": "",
				"Cat tree 2 level 3": "",
				"Image 2": images[1].replace('300x300', '600x600') if len(images) > 1 else '',
				"Image 3": images[2].replace('300x300', '600x600') if len(images) > 2 else '',
				"Image 4": images[3].replace('300x300', '600x600') if len(images) > 3 else '',
				"Image 5": images[4].replace('300x300', '600x600') if len(images) > 4 else '',
				"Sort order": "",
				"Attribute 1": '',
				"Attribute Value 1": '',
				"Attribute 2": '',
				"Attribute value 2": '',
				"Attribute 3": '',
				"Attribute value 3": '',
				"Attribute 4": '',
				"Attribute value 4": '',
				"Reviews": reviews,
				"Review link": response.url + '#tab-reviews' if reviews != '0' else '',
				"Rating": '',
				"Address": '',
				"p_id": self.p_id
			}
