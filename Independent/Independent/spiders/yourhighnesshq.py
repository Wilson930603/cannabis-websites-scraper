from Independent.spiders.base_spider import BaseSpider
import scrapy


class YourhighnesshqScraper(BaseSpider):
	name = 'yourhighnesshq'
	shop_name = 'Your Highness'
	start_urls = ['https://www.yourhighnesshq.com/pages/about-head-shop-london-waterloo-sarnia']
	p_id = 871465400

	def parse(self, response):
		social = '|'.join(response.xpath('(//ul[@class="social-media-icons"])[1]/li/a/@href').getall())
		img = response.xpath('//img[@id="logo"]/@src').get()
		desc = ' '.join(response.xpath('(//div[@class="ps-top-padding"])[2]/div/div/p/text()').getall())
		shops_data = response.xpath('//div[@class="copyright-powered"]//div[contains(@class,"columns large-4")]')
		phones = response.xpath('//a[@class="phone fi-telephone"]/text()').getall()[1:]
		i = 0
		for shop_data, phone in zip(shops_data, phones):
			address = shop_data.xpath('./a/span[2]/text()').get()
			addr, city, pro_zip = address.replace(', Canada', '').split(', ')
			province, postal_code = pro_zip.split(' ', 1)
			phone = phone.strip().replace('-', ' ')
			email = shop_data.xpath('./p[2]/a/text()').get()
			yield {
				"Producer ID": '',
				"p_id": self.p_id + i,
				"Producer": f"{self.shop_name} - {city}",
				"Description": desc,
				"Link": 'https://www.yourhighnesshq.com/pages/home',
				"SKU": "",
				"City": city,
				"Province": province,
				"Store Name": self.shop_name,
				"Postal Code": postal_code,
				"long": '',
				"lat": '',
				"ccc": "",
				"Page Url": 'https://www.yourhighnesshq.com/pages/home',
				"Active": "",
				"Main image": f'https:{img}',
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
			i += 1
		yield scrapy.Request('https://www.yourhighnesshq.com/pages/shop-now', dont_filter=True, callback=self.parse_cats)
		# yield scrapy.Request('https://yourhighnesscannabis.ca/about-us/', callback=self.parse_shop2)

	def parse_cats(self, response):
		cats = response.xpath('//a[@class="asim"]/@href').getall()
		if cats:
			cats = ['https://www.yourhighnesshq.com'+cat for cat in cats]
			for cat in cats:
				yield scrapy.Request(cat, callback=self.parse_cats)
		else:
			yield scrapy.Request(response.url, dont_filter=True, callback=self.parse_menu)


	def parse_shop2(self, response):
		desc = '\n'.join(response.xpath('//div[@data-id="398fa9be"]/div/p/text()').getall())
		social = '|'.join(response.xpath('//div[@class="ct-icon1 style1"]/a/@href').getall())
		phone = response.xpath('//a[@class="ct-contact-content ct-contact-link"]/text()').get().strip().rstrip()
		addr, city_zip = response.xpath('//span[@class="ct-contact-content"]/text()').get().strip().rstrip().split(', ')
		city, postal_code = city_zip.split(' ', 1)
		img = response.xpath('//a[@class="logo-mobile"]/img/@src').get()
		item = {
			"Producer ID": '',
			"p_id": self.p_id - 1,
			"Producer": f"{self.shop_name} - {city}",
			"Description": desc,
			"Link": 'https://yourhighnesscannabis.ca/',
			"SKU": "",
			"City": city,
			"Province": '',
			"Store Name": self.shop_name,
			"Postal Code": postal_code,
			"long": '',
			"lat": '',
			"ccc": "",
			"Page Url": 'https://yourhighnesscannabis.ca/',
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
			"Email": '',
			"Social": social,
			"FullAddress": "",
			"Address": addr,
			"Additional Info": "",
			"Created": "",
			"Comment": "",
			"Updated": ""
		}
		token_link = 'https://app.buddi.io/ropis/auth/get-token?domain=https:%2F%2Fyourhighnesscannabis.ca'
		yield scrapy.Request(token_link, callback=self.parse_token, meta={'item': item})

	def parse_token(self, response):
		item = response.meta['item']
		token = response.json()['token']
		headers = {
			'authority': 'app.buddi.io',
			'authorization-domain': 'https://yourhighnesscannabis.ca',
			'authorization': f'Bearer {token}'
		}
		yield scrapy.Request('https://app.buddi.io/ropis/auth/me', headers=headers, callback=self.parse_shop, meta={'item': item, 'headers': headers}, dont_filter=True)

	def parse_shop(self, response):
		headers = response.meta['headers']
		item = response.meta['item']
		data = response.json()
		lat = data['lat']
		long = data['long']
		item['lat'] = lat
		item['long'] = long
		item['Province'] = data['province']
		yield item
		page = 1
		yield scrapy.Request(f'https://app.buddi.io/ropis/menu?page={page}', headers=headers, meta={'headers': headers, 'page': page}, dont_filter=True, callback=self.parse_menu2)

	def parse_menu2(self, response):
		headers = response.meta['headers']
		page = response.meta['page'] + 1
		data = response.json()['data']
		for product in data:
			yield scrapy.Request(f'https://app.buddi.io/ropis/products/{product["id"]}', headers=headers, callback=self.parse_product2, dont_filter=True)
		if data:
			yield scrapy.Request(f'https://app.buddi.io/ropis/menu?page={page}', headers=headers, meta={'headers': headers, 'page': page}, dont_filter=True, callback=self.parse_menu2)

	def parse_product2(self, response):
		data = response.json()
		product_id = data['id']
		print(product_id)
		main_data = data["dispensary"][0]["sizes"][0]
		in_stock = "In Stock" if main_data['in_stock'] == 1 else "Out of Stock"
		stock_qt = main_data["inventory"]
		try:
			brand = data["brand_profile"]["name"]
		except:
			brand = ''
		yield {
			"Page URL": f"https://yourhighnesscannabis.ca/online-menu/#/product/{product_id}",
			"Brand": brand,
			"Name": data["name"],
			"SKU": "",
			"Out stock status": in_stock,
			"Stock count": stock_qt,
			"Currency": "CAD",
			"ccc": "",
			"Price": main_data["price"],
			"Manufacturer": self.shop_name,
			"Main image": data["images"][0]["public_path"],
			"Description": data["description"],
			"Product ID": product_id,
			"Additional Information": '',
			"Meta description": "",
			"Meta title": "",
			"Old Price": '',
			"Equivalency Weights": '',
			"Quantity": "",
			"Weight": f'{data["sizes"][0]["weight"]}{data["short_unit"]}',
			"Option": "",
			"Option type": '',
			"Option Value": "",
			"Option image": "",
			"Option price prefix": "",
			"Cat tree 1 parent": data["strain_type"],
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
			"Attribute 1": "CBD",
			"Attribute Value 1": f'{main_data["cbd"]}{data["thc_cbd_symbol"]}',
			"Attribute 2": "THC",
			"Attribute value 2": f'{main_data["thc"]}{data["thc_cbd_symbol"]}',
			"Attribute 3": "",
			"Attribute value 3": '',
			"Attribute 4": "",
			"Attribute value 4": "",
			"Reviews": '',
			"Review link": "",
			"Rating": '',
			"Address": '',
			"p_id": self.p_id - 1
		}

	def parse_menu(self, response):
		product_links = response.xpath('//li[@class="items"]/a/@href').getall()
		print(response.url)
		if product_links:
			for product_link in product_links:
				yield scrapy.Request(f'https://www.yourhighnesshq.com{product_link}', callback=self.parse_product)
		next_page = response.xpath('//span[@class="next"]/a/@href').get()
		if next_page:
			yield scrapy.Request(f'https://www.yourhighnesshq.com{next_page}', callback=self.parse_menu)

	def parse_product(self, response):
		img, name, url, desc = response.xpath('//meta[@property]/@content').getall()
		product_id = response.xpath('//input[@id="productId"]/@value').get().strip().rstrip()
		price = response.xpath('//span[@class="money"]/text()').get().replace('$', '')
		img = img.replace('http://www.yourhighnesshq.com//', 'https://')
		yield {
			"Page URL": url,
			"Brand": '',
			"Name": name,
			"SKU": '',
			"Out stock status": '',
			"Stock count": '',
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
			"Weight": '',
			"Option": "",
			"Option type": '',
			"Option Value": "",
			"Option image": "",
			"Option price prefix": "",
			"Cat tree 1 parent": "",
			"Cat tree 1 level 1": '',
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