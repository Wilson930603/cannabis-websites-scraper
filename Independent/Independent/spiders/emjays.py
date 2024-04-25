from Independent.spiders.base_spider import BaseSpider
import scrapy
import requests as r

class EmjaysSpider(BaseSpider):
	name = 'emjays'
	start_urls = []
	headers = {
		'cookie': 'em_did=6d6535723669646e6d677733734e61684c552f784d49743541426e45734b2f4a617249374f436f2f5852552b754954632f3537654f46742f3665553335624574; remember_me=MQ==; verifyAge=MQ==; _ga=GA1.1.233345592.1630433435; location=MQ==; active_category=Nw==; aul=MA==; active_cat=Nw==; XSRF-TOKEN=eyJpdiI6IkpaRU16OVFvMkMydzZGTW16MVQ1Q0E9PSIsInZhbHVlIjoicjZFOThNeWtxY2daWVg1elFMTytuZkVXR1Zwb0FFazR5dUltZzdEazMwNjJxOGdCSXRQWExHMEN6VGZnbVZRTmc3YzJ1XC9BZzRWclwvMHpSbkRFZGt3TkJrdkNsV0lvY0xuUFlzSjRGbmhiVk80MkdhOStPZmZudGk1ZEdYUDRYUyIsIm1hYyI6IjUzZTIwOThiOGNhMmEzZTk3YmZjZDI5ODI2OWRkYzU0MTU2NGNiMDY0YjkzMDAxYTIxMDMwZmE4ZjlhNzYzMGQifQ%3D%3D; em_jay_session=eyJpdiI6IlBJbGRrRGNFOGNjYldYN3pqXC9YVnJRPT0iLCJ2YWx1ZSI6Ijc2dHBGS2RJbkQrRklJVTNFZ2JXTkE3VG9RWkY1bmkrRE54cFkxZ3lNdExjK2YxK3I1Y2tnb3VGMDQxZDlkNjhWWmRuVDZhNkwrR3ZxTXBLYXpuQ0lQZ3o0QWgyYXFIQVduQkRIMzNtWTNzU1JnV01DUWh5Y3N6NGM4WDNaQnRvIiwibWFjIjoiNWViYjMxMjY3NmQ3ZGYwODYwNWY5YTYyZjg3MDNiZmM5YWE2NGZhZGJkNzcyYjNhMzI5MDk3ZTllMTRmODdmMiJ9; _ga_JHVFEEH65F=GS1.1.1631013620.6.1.1631013640.0'
	}
	default_data = {'device_id': '612e702d31add1630433325612e702d31adf', 'device_type': '1', 'location_id': '1'}
	shop_name = "Em Jay's"
	p_id = '763462130'

	def start_requests(self):
		yield scrapy.FormRequest('https://www.emjays.ca/api/locationList', callback=self.parse, headers=self.headers, formdata=self.default_data)

	def parse(self, response):
		location = response.json()['locations'][0]
		addr = location['name']
		city, province, postal_code = location['address'].split(', ')
		phone = location['phone']
		item = {
			"Producer ID": '',
			"p_id": self.p_id,
			"Producer": f"{self.shop_name} - {city}",
			"Description": "",
			"Link": 'https://www.emjays.ca/',
			"SKU": "",
			"City": city,
			"Province": province,
			"Store Name": self.shop_name,
			"Postal Code": postal_code,
			"long": '',
			"lat": '',
			"ccc": "",
			"Page Url": 'https://www.emjays.ca/',
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
			"Email": '',
			"Social": '',
			"FullAddress": "",
			"Address": addr,
			"Additional Info": "",
			"Created": "",
			"Comment": "",
			"Updated": ""
		}
		yield scrapy.Request('https://www.emjays.ca/web-home', headers=self.headers, callback=self.parse_additional, meta={'item': item})

	def parse_additional(self, response):
		item = response.meta['item']
		item['Main image'] = response.xpath('//img[@class="img-fluid main_logo"]/@src').get()
		item['Email'] = response.xpath('//a[@class="footer_mail"]/text()').get()
		item['Social'] = '|'.join(response.xpath('//ul[@class="footer_social"]/li/a/@href').getall())
		yield item
		data = self.default_data
		data['location_id'] = '1'
		yield scrapy.FormRequest('https://www.emjays.ca/api/listCategoryAttribute', callback=self.parse_categories, headers=self.headers, formdata=data)

	def parse_categories(self, response):
		categories = response.json()['category']
		for category in categories:
			for sub_category in category['sub_category']:
				category_id = sub_category['id']
				data = self.default_data
				data['category_id'] = str(category_id)
				data['user_id'] = '3'
				data['location_id'] = '1'
				data['filters'] = ''
				data['help_me_choose'] = ''
				data['search'] = ''
				data['sort_type'] = '1'
				data['get_filter_list'] = '1'
				data['skip'] = '0'
				data['take'] = '9999'
				yield scrapy.FormRequest('https://www.emjays.ca/api/productList', callback=self.parse_menu, headers=self.headers, formdata=data)

	def parse_menu(self, response):
		products = response.json()['products']
		for product in products:
			slug = product['slug_url']
			product_id = product['id']
			item = {
				"Page URL": f'https://www.emjays.ca/product/{slug}',
				"Brand": product['brand_name'],
				"Name": product['product_name'],
				"SKU": '',
				"Out stock status": '',
				"Stock count": '',
				"Currency": "CAD",
				"ccc": "",
				"Price": '',
				"Manufacturer": self.shop_name,
				"Main image": product['image'],
				"Description": '',
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
				"Cat tree 1 parent": product['category_name'],
				"Cat tree 1 level 1": '',
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
				"Attribute Value 1": "",
				"Attribute 2": '',
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
			data = self.default_data
			data['product_id'] = str(product_id)
			yield scrapy.FormRequest('https://www.emjays.ca/api/productDetails', callback=self.parse_product, headers=self.headers, formdata=data, meta={'item': item}, dont_filter=True)

	def parse_product(self, response):
		product = response.json()['products']
		item = response.meta['item']
		print(item['Page URL'])
		item['Description'] = product['product_long_description']
		nb_variations = len(product['variants'])
		if nb_variations > 1:
			item['Option type'] = "Choose an option"
		for variation in product['variants']:
			price = variation['price']
			weight = variation['size']
			qt = variation['available_quantity']
			status = 'In Stock'
			if qt == 0:
				status = 'Out of Stock'
			thc_name = 'THC'
			cbd_name = 'CBD'
			thc = f'{variation["thc"]}{variation["thc_type"]}'
			cbd = f'{variation["cbd"]}{variation["cbd_type"]}'
			item['Out stock status'] = status
			item['Stock count'] = qt
			item['Price'] = price
			item['Weight'] = weight
			item["Attribute 1"] = thc_name
			item["Attribute Value 1"] = thc
			item["Attribute 2"] = cbd_name
			item["Attribute value 2"] = cbd
			if nb_variations > 1:
				item['Option Value'] = weight
				item['Option price prefix'] = price
			yield item
