from Independent.spiders.base_spider import BaseSpider
import scrapy


class AxessmokeScraper(BaseSpider):
	name = 'axessmoke'
	start_urls = ['https://axessmoke.com/']
	p_id = '17843682'

	def parse(self, response):
		name = 'Axes Smoke'
		full_addr = response.xpath('(//div[@class="bt_bb_service_content_text"])[1]/text()').get()
		addr, city, province = full_addr.split(', ')
		email = response.xpath('(//div[@class="bt_bb_service_content_text"])[2]/text()').get()
		phones = response.xpath('(//div[@class="bt_bb_service_content_text"])[4]/text()').getall()
		img = response.xpath('//img[@class="btMainLogo"]/@src').get()
		img2 = response.xpath('//img[@class="btAltLogo"]/@src').get()
		social = '|'.join(response.xpath('(//div[@class="bt_bb_column_content "])[20]/div/a/@href').getall()[0:2])
		yield {
			"Producer ID": '',
			"p_id": self.p_id,
			"Producer": f"{name} - {city}",
			"Description": '',
			"Link": "https://axessmoke.com/",
			"SKU": "",
			"City": city,
			"Province": province,
			"Store Name": name,
			"Postal Code": "M6J 1H7",
			"long": "",
			"lat": "",
			"ccc": "",
			"Page Url": "https://axessmoke.com/",
			"Active": "",
			"Main image": img,
			"Image 2": img2,
			"Image 3": "",
			"Image 4": '',
			"Image 5": '',
			"Type": "",
			"License Type": "",
			"Date Licensed": "",
			"Phone": phones[0].strip(),
			"Phone 2": phones[1].strip(),
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
		yield scrapy.Request(f'http://api-g.weedmaps.com/discovery/v1/listings/dispensaries/axes-smoke-cannabis/menu_items?page_size=150&page=1', callback=self.parse_products)

	def parse_products(self, response):
		products = response.json()['data']['menu_items']
		brands = self.settings.get('BRANDS', [])
		brands_lower = [x.lower() for x in brands]
		if len(products) >= 150:
			first_url, next_page = response.url.split('&page=')
			next_page = int(next_page) + 1
			yield scrapy.Request(f"{first_url}&page={next_page}", callback=self.parse_products)
		for product in products:
			eq_weight = ''
			if len(product['prices']) == 1:
				qty = ''
				weight = ''
			else:
				try:
					qty = str(product['prices'][0]['units'])
					weight = product['prices'][0]['label']
				except:
					try:
						qty = str(product['prices']['unit']['units'])
						weight = product['prices']['unit']['label']
					except:
						try:
							qty = str(product['prices']['ounce'][0]['units'])
							weight = product['prices']['ounce'][0]['label']
						except:
							qty = str(product['prices']['gram'][0]['units'])
							weight = product['prices']['gram'][0]['label']
			if product['price']:
				price = str(product['price']['price'])
				old_price = str(product['price']['original_price'])
				if price == old_price:
					old_price = ''
			else:
				price = ''
				old_price = ''
			try:
				brand = product['brand_endorsement']['brand_name']
			except:
				brand = ''
				if '-' in product["name"]:
					brand = product['name'].split(' - ', 1)[0]
			if brand and brands and brand.lower() not in brands_lower:
				self.logger.debug(f'Ignore brand: {brand}')
				continue
			try:
				product_id = product['brand_endorsement']['product_id']
			except:
				product_id = ''
			item = {
				"Page URL": f"https://weedmaps.com/dispensaries/axes-smoke-cannabis/menu/{product['slug']}",
				"Brand": brand,
				"Name": product["name"],
				"SKU": product["id"],
				"Out stock status": 'In Stock',
				"Stock count": '',
				"Currency": "CAD",
				"ccc": "",
				"Price": price,
				"Manufacturer": '',
				"Main image": product['avatar_image']['original_url'],
				"Description": '',
				"Product ID": product_id,
				"Additional Information": '',
				"Meta description": "",
				"Meta title": "",
				"Old Price": old_price,
				"Equivalency Weights": '',
				"Quantity": qty,
				"Weight": weight,
				"Option": "",
				"Option type": '',
				"Option Value": "",
				"Option image": "",
				"Option price prefix": "",
				"Cat tree 1 parent": product["category"]['name'],
				"Cat tree 1 level 1": '',
				"Cat tree 1 level 2": "",
				"Cat tree 2 parent": '',
				"Cat tree 2 level 1": "",
				"Cat tree 2 level 2": "",
				"Cat tree 2 level 3": "",
				"Image 2": product['avatar_image']['large_url'],
				"Image 3": '',
				"Image 4": '',
				"Image 5": '',
				"Sort order": "",
				"Attribute 1": "",
				"Attribute Value 1": "",
				"Attribute 2": "",
				"Attribute value 2": "",
				"Attribute 3": "",
				"Attribute value 3": '',
				"Attribute 4": "",
				"Attribute value 4": "",
				"Reviews": product['reviews_count'],
				"Review link": "",
				"Rating": product['rating'],
				"Address": '',
				"p_id": self.p_id
			}
			yield scrapy.Request(f"http://api-g.weedmaps.com/discovery/v1/listings/dispensaries/axes-smoke-cannabis/menu_items/{product['slug']}", meta={'item': item}, callback=self.get_description)

	def get_description(self, response):
		item = response.meta['item']
		description = response.json()["data"]["menu_item"]["body"].strip().rstrip()
		item['Description'] = description
		yield item
