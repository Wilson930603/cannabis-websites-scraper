from Independent.spiders.base_spider import BaseSpider
import scrapy


class StellarBudScraper(BaseSpider):
	name = 'stellarbud'
	p_id = '95231702'
	shop_name = 'Stellar Bud'
	headers = {
		'cookie': 'age_gate=19; yith_wcwl_session_c6287695344ffbe37bf227703fefa5af=%7B%22session_id%22%3A%22e17c91c394d1f779d1ad6fb6ef2b0d7a%22%2C%22session_expiration%22%3A1636911081%2C%22session_expiring%22%3A1636907481%2C%22cookie_hash%22%3A%2225c5951547d52ba9de4013fd87c14ac3%22%7D'
	}

	def start_requests(self):
		yield scrapy.Request('https://stellarbud.ca/about-us/', headers=self.headers, callback=self.parse)

	def parse(self, response):
		main_image = response.xpath('//div[@class="logo"]/a/img/@src').get()
		description = response.xpath('(//div[@class="wpb_wrapper"])[11]/p/text()').get()
		contact = response.xpath('(//div[@class="wpb_wrapper"])[19]/p/text()').getall()
		address = contact[0].split(' ', 1)[1][0:-1]
		address, postal_code = address.rsplit(' ', 1)
		city = 'Woodstock'
		email = contact[1].split(' ')[1]
		phone = response.xpath('(//div[@class="wpb_wrapper"])[18]/h3/text()').get().replace('+', '').replace('-', ' ')
		yield {
			"Producer ID": '',
			"p_id": self.p_id,
			"Producer": f"{self.shop_name} - {city}",
			"Description": description,
			"Link": 'https://stellarbud.ca/',
			"SKU": "",
			"City": city,
			"Province": 'ON',
			"Store Name": self.shop_name,
			"Postal Code": postal_code,
			"long": '',
			"lat": '',
			"ccc": "",
			"Page Url": 'https://stellarbud.ca/',
			"Active": "",
			"Main image": main_image,
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
			"Address": address,
			"Additional Info": "",
			"Created": "",
			"Comment": "",
			"Updated": ""
		}
		yield scrapy.Request('https://stellarbud.ca/shop/', callback=self.parse_menu, headers=self.headers)

	def parse_menu(self, response):
		links = response.xpath('//div[@class="product-wrapper gridview"]//a[@class="woocommerce-LoopProduct-link woocommerce-loop-product__link"]/@href').getall()
		for link in links:
			yield scrapy.Request(link, callback=self.parse_product, headers=self.headers)
		next_link = response.xpath('//a[@class="next page-numbers"]/@href').get()
		if next_link:
			yield scrapy.Request(next_link, callback=self.parse_menu, headers=self.headers)

	def parse_product(self, response):
		name = response.xpath('//h1[@class="product_title entry-title"]/text()').get()
		price = response.xpath('//p[@class="price"]/span/bdi/text()').get()
		img = response.xpath('//a[@itemprop="image"]/@href').get()
		brand = ''
		thc_name = ''
		thc = ''
		cbd_name = ''
		cbd = ''
		cat_name = ''
		dsc = response.xpath('//div[@class="woocommerce-product-details__short-description"]/p/text()').getall()
		for x in dsc:
			y = x.strip().rstrip()
			try:
				n, v = y.split(' : ')
			except:
				continue
			if n == 'Species':
				cat_name = v
			elif n == 'Brand':
				brand = v
			elif n == 'THC':
				thc_name = 'THC'
				thc = v
			elif n == 'CBD':
				cbd_name = 'CBD'
				cbd = v
		desc = response.xpath('//div[@id="tab-description"]/p/text()').get()
		sku = response.xpath('//span[@class="sku"]/text()').get()
		product_id = response.xpath('//button[@name="add-to-cart"]/@value').get()
		stock = response.xpath('//p[@class="stock in-stock"]/text()').get()
		in_stock = 'Out of Stock'
		stock_qt = 0
		if stock:
			in_stock = 'In Stock'
			stock_qt = int(stock.replace(' in stock', ''))
		weight = ''
		try:
			weight = sku.split('_', 1)[1].split('___')[0]
			if weight == sku:
				weight = ''
		except:
			pass
		print(response.url)
		yield {
			"Page URL": response.url,
			"Brand": brand,
			"Name": name,
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
			"Cat tree 1 parent": cat_name,
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
			"Attribute 1": cbd_name,
			"Attribute Value 1": cbd,
			"Attribute 2": thc_name,
			"Attribute value 2": thc,
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
