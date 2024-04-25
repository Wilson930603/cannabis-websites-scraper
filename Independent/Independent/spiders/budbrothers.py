import json

from Independent.spiders.base_spider import BaseSpider
import scrapy


class BudbrothersScraper(BaseSpider):
	name = 'budbrothers'
	start_urls = ['https://budbrothers.ca/shop/']
	p_id = '65311940'
	shop_name = 'Bud Brothers'

	def parse(self, response):
		img = response.xpath('//div[@class="site-logo"]/a/img/@src').get()
		yield {
			"Producer ID": '',
			"p_id": self.p_id,
			"Producer": f"{self.shop_name}",
			"Description": "",
			"Link": 'https://budbrothers.ca/',
			"SKU": "",
			"City": '',
			"Province": '',
			"Store Name": self.shop_name,
			"Postal Code": '',
			"long": '',
			"lat": '',
			"ccc": "",
			"Page Url": 'https://budbrothers.ca/',
			"Active": "",
			"Main image": img,
			"Image 2": "",
			"Image 3": "",
			"Image 4": '',
			"Image 5": '',
			"Type": "",
			"License Type": "",
			"Date Licensed": "",
			"Phone": '',
			"Phone 2": "",
			"Contact Name": "",
			"EmailPrivate": "",
			"Email": '',
			"Social": 'https://www.facebook.com/Bud-Brothers-Canada-103235851760895/',
			"FullAddress": "",
			"Address": '',
			"Additional Info": "",
			"Created": "",
			"Comment": "",
			"Updated": ""
		}
		categories = response.xpath('//li[@class="product-category product first default"]/a/@href').getall()
		for category_link in categories:
			yield scrapy.Request(category_link, callback=self.parse_category)

	def parse_category(self, response):
		products = response.xpath('//a[@class="nv-product-overlay-link"]/@href').getall()
		for product_link in products:
			yield scrapy.Request(product_link, callback=self.parse_product)
		next_page = response.xpath('//a[@class="next page-numbers"]/@href').get()
		if next_page:
			yield scrapy.Request(next_page, callback=self.parse_category)

	def parse_product(self, response):
		print(response.url)
		category = response.xpath('//a[@rel="tag"]/text()').get()
		name = response.xpath('//h1/text()').get()
		old_price = ''
		price = response.xpath('//p[@class="price"]/span/bdi/text()').get()
		if not price:
			price = response.xpath('//p[@class="price"]/ins/span/bdi/text()').get()
			old_price = response.xpath('//p[@class="price"]/del/span/bdi/text()').get()
		img = response.xpath('//div[@class="woocommerce-product-gallery__image"]/@data-thumb').get()
		product_id = response.xpath('//link[@rel="alternate" and contains(@href, "v2/product")]/@href').get().split('/')[-1]
		desc = response.xpath('//meta[@property="og:description"]/@content').get()
		lines = desc.splitlines()
		desc = ''
		for line in lines:
			ln = line.strip().rstrip()
			if ln:
				desc += f'{ln}\n'
		desc = desc.rstrip()
		status = response.xpath('//meta[@property="og:availability"]/@content').get()
		if status == "instock":
			status = "In Stock"
		else:
			status = "Out of Stock"
		item = {
			"Page URL": response.url,
			"Brand": '',
			"Name": name,
			"SKU": '',
			"Out stock status": status,
			"Stock count": "",
			"Currency": "CAD",
			"ccc": "",
			"Price": price,
			"Manufacturer": '',
			"Main image": img,
			"Description": desc,
			"Product ID": product_id,
			"Additional Information": "",
			"Meta description": "",
			"Meta title": "",
			"Old Price": old_price,
			"Equivalency Weights": "",
			"Quantity": '',
			"Weight": '',
			"Option": "",
			"Option type": "",
			"Option Value": "",
			"Option image": "",
			"Option price prefix": "",
			"Cat tree 1 parent": category,
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
			"Attribute 2": "",
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
		variation_data = response.xpath('//form[@class="variations_form cart"]/@data-product_variations').get()
		if variation_data:
			variation_data = variation_data.replace('<p class=\"stock in-stock\">In stock<\/p>', '').replace('\n', '')
			variation_json = json.loads(variation_data)
			first_item = variation_json[0]
			item["SKU"] = first_item["sku"]
			item["Weight"] = first_item["weight_html"]
			if item["Weight"] == 'N/A':
				item["Weight"] = ""
			item["Stock count"] = first_item['max_qty']
			if first_item["is_in_stock"]:
				item["Out stock status"] = 'In Stock'
			else:
				item["Out stock status"] = 'Out of Stock'
			if len(variation_json) == 1:
				yield item
			else:
				item["Option type"] = "Choose a size"
				for variant in variation_json:
					if variant["is_in_stock"]:
						item["Out stock status"] = 'In Stock'
					else:
						item["Out stock status"] = 'Out of Stock'
					item["SKU"] = variant["sku"]
					item["Option Value"] = variant["weight_html"]
					if item["Option Value"] == 'N/A':
						item["Option Value"] = ''
						item["Weight"] = ''
					item["Option price prefix"] = variant["display_price"]
					item["Price"] = variant["display_price"]
					yield item
		else:
			yield item

