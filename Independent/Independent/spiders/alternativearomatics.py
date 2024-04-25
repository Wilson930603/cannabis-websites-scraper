import json

from Independent.spiders.base_spider import BaseSpider
import scrapy


class AlternativearomaticsScraper(BaseSpider):
	name = 'alternativearomatics'
	p_id = '97835287'
	start_urls = ['https://www.alternativearomatics.ca/']

	def parse(self, response):
		address, city_pro = response.xpath('//span[@id="fancy-title-40"]/span/p/text()').get().split(', ')
		city, province = city_pro.split(' ')
		name = response.xpath('//h2[@id="fancy-title-37"]/span/p/text()').get()
		link = response.xpath('//div[@id="mk-button-41"]/a/@href').get()
		phone = response.xpath('//h2[@id="fancy-title-54"]/span/p/text()').get().split(': ')[1]
		email = response.xpath('//h2[@id="fancy-title-56"]/span/p/text()').get().split(': ')[1]
		logo = response.xpath('//img[@class="mk-desktop-logo dark-logo "]/@src').get()
		logo2 = response.xpath('//img[@class="mk-sticky-logo "]/@src').get()
		img = response.xpath('//img[@title="esquimalt-store"]/@src').get()
		desc = response.xpath('//div[@id="text-block-19"]/p/text()').get()
		yield {
			"Producer ID": '',
			"p_id": self.p_id,
			"Producer": f"Alternative Aromatics Ltd. - {name}",
			"Description": desc,
			"Link": link,
			"SKU": "",
			"City": city,
			"Province": province,
			"Store Name": "Alternative Aromatics Ltd.",
			"Postal Code": "V9A 2N4",
			"long": "",
			"lat": "",
			"ccc": "",
			"Page Url": link,
			"Active": "",
			"Main image": img,
			"Image 2": logo,
			"Image 3": logo2,
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
			"Social": '',
			"FullAddress": "",
			"Address": address,
			"Additional Info": "",
			"Created": "",
			"Comment": "",
			"Updated": ""
		}
		yield scrapy.Request('https://www.alternativearomatics.ca/quadra/', callback=self.parse_menu)

	def parse_menu(self, response):
		product_links = response.xpath('//a[@class="woocommerce-LoopProduct-link woocommerce-loop-product__link"]/@href').getall()
		for product_link in product_links:
			yield scrapy.Request(product_link, callback=self.parse_products)
		next_link = response.xpath('//a[@class="next page-numbers"]/@href').get()
		if next_link:
			yield scrapy.Request(next_link, callback=self.parse_menu)

	def parse_products(self, response):
		print(response.url)
		category = response.xpath('//a[@rel="tag"]/text()').get()
		name = response.xpath('//h1/text()').get()
		price = response.xpath('//p[@class="price"]//text()').getall()[1]
		img = response.xpath('//div[@class="woocommerce-product-gallery__image"]/@data-thumb').get()
		product_id = response.xpath('//link[@rel="alternate" and contains(@href, "v2/product")]/@href').get().split('/')[-1]
		desc = response.xpath('//meta[@property="og:description"]/@content').get()
		item = {
			"Page URL": response.url,
			"Brand": '',
			"Name": name,
			"SKU": '',
			"Out stock status": 'Out of Stock',
			"Stock count": '0',
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
			"Old Price": '',
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
					item["Stock count"] = variant['max_qty']
					item["SKU"] = variant["sku"]
					item["Option Value"] = variant["weight_html"]
					if item["Option Value"] == 'N/A':
						item["Option Value"] = ''
					item["Option price prefix"] = variant["display_price"]
					yield item
		else:
			yield item
