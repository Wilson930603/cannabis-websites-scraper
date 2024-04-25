from Independent.spiders.base_spider import BaseSpider
import scrapy


class CanNaBisSpider(BaseSpider):
	name = 'can-na-bis'
	shop_name = 'Can-Na-Bis'
	start_urls = ['https://can-na-bis.ca/']
	p_id = 420831119

	def parse(self, response):
		phone, addr, city, province = response.xpath('//small[@class="site-footer__copyright-content site-footer__copyright-content-powered-by"]/text()').get().replace('-', ' ').replace('\n', ' ').replace(' CANADA', '').strip().split(', ')
		yield {
			"Producer ID": '',
			"p_id": self.p_id,
			"Producer": f"{self.shop_name} - {city}",
			"Description": '',
			"Link": 'https://can-na-bis.ca/',
			"SKU": "",
			"City": city,
			"Province": province,
			"Store Name": self.shop_name,
			"Postal Code": '',
			"long": '',
			"lat": '',
			"ccc": "",
			"Page Url": 'https://can-na-bis.ca/',
			"Active": "",
			"Main image": '',
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
			"Email": "",
			"Social": '',
			"FullAddress": "",
			"Address": addr,
			"Additional Info": "",
			"Created": "",
			"Comment": "",
			"Updated": ""
		}
		collections = response.xpath('//a[@class="collection-grid-item__link"]/@href').getall()
		for collection in collections:
			page = 1
			link = f'https://can-na-bis.ca{collection}?page={page}'
			yield scrapy.Request(link, callback=self.parse_menu, meta={'page': page, 'collection': collection})

	def parse_menu(self, response):
		print(response.url)
		page = response.meta['page']
		collection = response.meta['collection']
		products = response.xpath('//a[@class="grid-view-item__link grid-view-item__image-container full-width-link"]/@href').getall()
		for product in products:
			product_link = f'https://can-na-bis.ca{product}'
			yield scrapy.Request(product_link, callback=self.parse_product)
		if products:
			page += 1
			link = f'https://can-na-bis.ca{collection}?page={page}'
			yield scrapy.Request(link, callback=self.parse_menu, meta={'page': page, 'collection': collection})

	def parse_product(self, response):
		print(response.url)
		name = response.xpath('//meta[@property="og:title"]/@content').get()
		desc = response.xpath('//meta[@property="og:description"]/@content').get()
		price = response.xpath('//meta[@property="og:price:amount"]/@content').get()
		img = response.xpath('//meta[@property="og:image:secure_url"]/@content').get()
		product_id = response.xpath('//form[@method="post"]/@id').get().split('_')[-1]
		sold_out = response.xpath('//button[@name="add"]/@aria-label').get()
		in_stock = 'In Stock'
		if sold_out == 'Sold out':
			in_stock = 'Out of Stock'
		old_price = response.xpath('//div[@class="product__price"]//s[@class="price-item price-item--regular"]/text()').get().replace('$', '').strip().rstrip()
		weight = response.xpath('//li[contains(text(), "Weight")]/text()').get()
		if weight:
			weight = weight.split(' : ')[1].rstrip()
		yield {
			"Page URL": response.url,
			"Brand": '',
			"Name": name,
			"SKU": '',
			"Out stock status": in_stock,
			"Stock count": "",
			"Currency": "CAD",
			"ccc": "",
			"Price": price,
			"Manufacturer": self.shop_name,
			"Main image": img,
			"Description": desc,
			"Product ID": product_id,
			"Additional Information": "",
			"Meta description": "",
			"Meta title": "",
			"Old Price": old_price,
			"Equivalency Weights": "",
			"Quantity": '',
			"Weight": weight,
			"Option": "",
			"Option type": "",
			"Option Value": "",
			"Option image": "",
			"Option price prefix": "",
			"Cat tree 1 parent": '',
			"Cat tree 1 level 1": '',
			"Cat tree 1 level 2": "",
			"Cat tree 2 parent": "",
			"Cat tree 2 level 1": "",
			"Cat tree 2 level 2": "",
			"Cat tree 2 level 3": "",
			"Image 2": '',
			"Image 3": '',
			"Image 4": '',
			"Image 5": '',
			"Sort order": "",
			"Attribute 1": '',
			"Attribute Value 1": '',
			"Attribute 2": '',
			"Attribute value 2": '',
			"Attribute 3": "",
			"Attribute value 3": '',
			"Attribute 4": "",
			"Attribute value 4": "",
			"Reviews": '',
			"Review link": "",
			"Rating": '',
			"Address": '',
			"p_id": self.p_id
		}
