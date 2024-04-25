import json
import re

from Independent.spiders.base_spider import BaseSpider
import scrapy


class BestbudsforeverScraper(BaseSpider):
	name = 'bestbudsforever'
	p_id = '75820714'
	img = 'https://bestbudsforever.ca/wp-content/uploads/2017/10/bestbud-logo.png'

	def start_requests(self):
		yield scrapy.Request('https://bestbudsforever.ca/', callback=self.parse)

	def parse_empty(self, response):
		pass

	def parse(self, response):
		name = 'Best Buds Forever'
		desc = " ".join(response.xpath('//div[@id="row-1881067490"]/div/div/p//text()').getall())
		contact = response.xpath('//ul[@id="header-contact"]/li')
		full_addr = contact[0].xpath('./a/@href').get().split('Store: ')[1]
		addr, city, postal_code = full_addr.rsplit(', ', 2)
		province, postal_code = postal_code.split(' ', 1)
		email = contact[1].xpath('./a/@href').get().split(':')[1]
		phone = contact[3].xpath('./a/@href').get().split(':')[1].replace('+', '').replace('-', ' ')
		social = "|".join(response.xpath('//div[@class="social-icons follow-icons "]/a/@href').getall()[0:3])
		yield {
			"Producer ID": '',
			"p_id": self.p_id,
			"Producer": f"{name} - {city}",
			"Description": desc,
			"Link": "https://bestbudsforever.ca/",
			"SKU": "",
			"City": city,
			"Province": province,
			"Store Name": name,
			"Postal Code": postal_code,
			"long": "",
			"lat": "",
			"ccc": "",
			"Page Url": "https://bestbudsforever.ca/",
			"Active": "",
			"Main image": self.img,
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
			"Social": social,
			"FullAddress": "",
			"Address": addr,
			"Additional Info": "",
			"Created": "",
			"Comment": "",
			"Updated": ""
		}
		item = {
			"Producer ID": '',
			"p_id": "",
			"Producer": "",
			"Description": desc,
			"Link": "",
			"SKU": "",
			"City": "",
			"Province": "",
			"Store Name": name,
			"Postal Code": "",
			"long": "",
			"lat": "",
			"ccc": "",
			"Page Url": "",
			"Active": "",
			"Main image": self.img,
			"Image 2": "",
			"Image 3": "",
			"Image 4": '',
			"Image 5": '',
			"Type": "",
			"License Type": "",
			"Date Licensed": "",
			"Phone": "",
			"Phone 2": "",
			"Contact Name": "",
			"EmailPrivate": "",
			"Email": email,
			"Social": social,
			"FullAddress": "",
			"Address": "",
			"Additional Info": "",
			"Created": "",
			"Comment": "",
			"Updated": ""
		}
		yield scrapy.Request('https://bestbudsforever.ca/best-buds-forever-toronto-queen-st-west/', callback=self.parse_empty, meta={'p_id': '75820715', 'item': item})
		yield scrapy.Request('https://bestbudsforever.ca/junction/', callback=self.parse_empty, meta={'p_id': '75820716', 'item': item})
		yield scrapy.Request('https://bestbudsforever.ca/woodbine-mall/', callback=self.parse_empty, meta={'p_id': '75820717', 'item': item})
		yield scrapy.Request("https://bestbudsforever.ca/shop/", callback=self.parse_menu)

	def parse_empty(self, response):
		p_id = response.meta['p_id']
		item = response.meta['item']
		all_addr = response.xpath('//div[@class="map_inner map-inner last-reset absolute x100 md-x5 lg-x5 y100 md-y95 lg-y95"]/p/strong/text()').getall()
		addr = all_addr[1].rstrip()
		city, province = all_addr[2].split(', ')
		postal_code = all_addr[3]
		item["Link"] = response.url
		item["Page Url"] = response.url
		item['p_id'] = p_id
		item["Address"] = addr
		item["Producer"] = f'Best Buds Forever - {city}'
		item["City"] = city
		item["Province"] = province
		item["Postal Code"] = postal_code
		phone = response.xpath('//div[@class="map_inner map-inner last-reset absolute x100 md-x5 lg-x5 y100 md-y95 lg-y95"]/p[1]/a/text()').get()
		if phone:
			item["Phone"] = phone.replace('-', ' ')
		yield item

	def parse_menu(self, response):
		print(response.url)
		product_links = response.xpath('//p[@class="name product-title"]/a/@href').getall()
		for product_link in product_links:
			print(product_link)
			yield scrapy.Request(product_link, callback=self.parse_product)
		next_page = response.xpath('//a[@class="next page-number"]/@href').get()
		if next_page:
			yield scrapy.Request(next_page, callback=self.parse_menu)

	def parse_product(self, response):
		name = response.xpath('//h1/text()').get().strip().rstrip()
		price = response.xpath('//div[@class="price-wrapper"]/p/span/bdi/text()').get()
		old_price = ''
		if not price:
			prices = response.xpath('//div[@class="price-wrapper"]/p//span/bdi/text()').getall()
			if prices:
				old_price = prices[0]
				price = prices[1]
		stock = response.xpath('//p[@class="stock in-stock"]/text()').get()
		in_stock = 'Out of Stock'
		stock_qt = 0
		if stock:
			in_stock = 'In Stock'
			stock_qt = int(stock.replace(' in stock', ''))
		sku = response.xpath('//span[@class="sku"]/text()').get()
		desc = response.xpath('//div[@class="product-short-description"]//text()').getall()
		final_desc = ''
		for dsc in desc:
			dsc = dsc.strip().rstrip()
			if dsc:
				final_desc += dsc + '\n'
		final_desc = final_desc.rstrip()
		product_id = response.xpath('//a[@class="add_to_wishlist single_add_to_wishlist"]/@href').get().split('=')[1]
		categories = response.xpath('//span[@class="posted_in"]/a/text()').getall()
		img = response.xpath('//meta[@property="og:image"]/@content').get()
		size = re.search('Size: .+', final_desc)
		if size:
			size = size.group(0).replace('Size: ', '')
		else:
			size = ''
		item = {
			"Page URL": response.url,
			"Brand": "",
			"Name": name,
			"SKU": sku,
			"Out stock status": in_stock,
			"Stock count": stock_qt,
			"Currency": "CAD",
			"ccc": "",
			"Price": price,
			"Manufacturer": 'Best Buds Forever',
			"Main image": img,
			"Description": final_desc,
			"Product ID": product_id,
			"Additional Information": '',
			"Meta description": "",
			"Meta title": "",
			"Old Price": old_price,
			"Equivalency Weights": '',
			"Quantity": "",
			"Weight": size,
			"Option": "",
			"Option type": '',
			"Option Value": "",
			"Option image": "",
			"Option price prefix": "",
			"Cat tree 1 parent": categories[0],
			"Cat tree 1 level 1": "",
			"Cat tree 1 level 2": "",
			"Cat tree 2 parent": '',
			"Cat tree 2 level 1": "",
			"Cat tree 2 level 2": "",
			"Cat tree 2 level 3": "",
			"Image 2": "",
			"Image 3": "",
			"Image 4": "",
			"Image 5": "",
			"Sort order": "",
			"Attribute 1": "",
			"Attribute Value 1": "",
			"Attribute 2": "",
			"Attribute value 2": "",
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
				item["Option type"] = "Choose an option"
				for variant in variation_json:
					item["Main image"] = variant["image"]["url"]
					if variant["is_in_stock"]:
						item["Out stock status"] = 'In Stock'
					else:
						item["Out stock status"] = 'Out of Stock'
					item["Stock count"] = variant['max_qty']
					item["SKU"] = variant["sku"]
					item["Option Value"] = variant["attributes"][list(variant["attributes"].keys())[0]]
					if item["Option Value"] == 'N/A':
						item["Option Value"] = ''
					item["Option price prefix"] = variant["display_price"]
					yield item
		else:
			imgs = response.xpath('(//div[@class="flickity-viewport"])[2]/div/div/a/img/@src').getall()
			img_ = ['', '', '', '', '']
			for i in range(0, min(5, len(imgs))):
				img_[i] = imgs[i]
			item["Image 2"] = img_[1]
			item["Image 3"] = img_[2]
			item["Image 4"] = img_[3]
			item["Image 5"] = img_[4]
			yield item

