import json

from Independent.spiders.base_spider import BaseSpider
import scrapy


class ThePotShackSpider(BaseSpider):
	name = 'thepotshack'
	shop_name = 'The Pot Shack'
	p_id = 18798203
	start_urls = ['https://www.thepotshack.ca/contact-us/']

	def parse(self, response):
		addr, city, province = response.xpath('(//div[@class="wpb_text_column wpb_content_element  snow"])[1]/div/p/text()[1]').get().rsplit(', ', 2)
		phone = response.xpath('//div[@class="la-contact-item la-contact-phone"]/span/text()').get().replace('-', ' ')
		email = response.xpath('//div[@class="la-contact-item la-contact-email"]/span/text()').get()
		yield {
			"Producer ID": '',
			"p_id": self.p_id,
			"Producer": f"{self.shop_name} - {city}",
			"Description": '',
			"Link": 'https://www.thepotshack.ca/',
			"SKU": "",
			"City": city,
			"Province": 'SK',
			"Store Name": self.shop_name,
			"Postal Code": 'S7H 4G2',
			"long": '',
			"lat": '',
			"ccc": "",
			"Page Url": 'https://www.thepotshack.ca/',
			"Active": "",
			"Main image": 'https://www.thepotshack.ca/wp-content/uploads/2018/12/ThePotShack_Logo.png',
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
			"Social": '',
			"FullAddress": "",
			"Address": addr,
			"Additional Info": "",
			"Created": "",
			"Comment": "",
			"Updated": ""
		}
		yield scrapy.Request('https://www.thepotshack.ca/shop/?per_page=30', callback=self.parse_menu)

	def parse_menu(self, response):
		products = response.xpath('//ul[@data-item_selector=".product_item"]//a[@class="woocommerce-LoopProduct-link woocommerce-loop-product__link"]/@href').getall()
		for product_link in products:
			yield scrapy.Request(product_link, callback=self.parse_product)
		next_page = response.xpath('//a[@class="next page-numbers"]/@href').get()
		if next_page:
			yield scrapy.Request(next_page, callback=self.parse_menu)

	def parse_product(self, response):
		print(response.url)
		product_id = response.xpath('//link[@rel="shortlink"]/@href').get().split('=')[1]
		img = response.xpath('//div[@class="woocommerce-product-gallery__image"]/a/@href').get()
		product_name = response.xpath('//h1[@class="product_title entry-title"]/text()').get()
		cat = response.xpath('//span[@class="posted_in"]/a[@rel="tag"]/text()').get()
		desc = response.xpath('//div[@id="tab-description"]/div[@class="tab-content"]/p/text()').get()
		weight = response.xpath('//tr[@class="woocommerce-product-attributes-item woocommerce-product-attributes-item--weight"]/td/text()').get()
		price = response.xpath('//div[@class="single-price-wrapper"]//bdi/text()').get()
		stock_qt = response.xpath('//input[@name="quantity"]/@max').get()
		if stock_qt:
			if int(stock_qt) > 0:
				in_stock = 'In Stock'
			else:
				in_stock = 'Out of Stock'
		else:
			in_stock = 'Out of Stock'
			stock_qt = 0
		sku = response.xpath('//span[@class="sku"]/text()').get()
		item = {
			"Page URL": response.url,
			"Brand": '',
			"Name": product_name,
			"SKU": sku,
			"Out stock status": in_stock,
			"Stock count": stock_qt,
			"Currency": "CAD",
			"ccc": "",
			"Price": price,
			"Manufacturer": self.shop_name,
			"Main image": img,
			"Description": desc,
			"Product ID": product_id,
			"Additional Information": '',
			"Meta description": "",
			"Meta title": "",
			"Old Price": '',
			"Equivalency Weights": '',
			"Quantity": "",
			"Weight": weight,
			"Option": "",
			"Option type": '',
			"Option Value": "",
			"Option image": "",
			"Option price prefix": "",
			"Cat tree 1 parent": cat,
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
		variation_data = response.xpath('//form[contains(@class,"variations_form cart")]/@data-product_variations').get()
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

