from Independent.spiders.base_spider import BaseSpider
import scrapy


class LyonsRoarSpider(BaseSpider):
	name = 'lyonsroar'
	shop_name = "Lyon's Roar"
	p_id = 8265810
	start_urls = ['https://app.buddi.io/ropis/auth/get-token?domain=https:%2F%2Fwww.lyonsroar.ca']

	def parse(self, response):
		token = response.json()['token']
		headers = {
			'authority': 'app.buddi.io',
			'authorization-domain': 'https://www.lyonsroar.ca',
			'authorization': f'Bearer {token}'
		}
		yield scrapy.Request('https://app.buddi.io/ropis/auth/me', headers=headers, callback=self.parse_shop, meta={'headers': headers})

	def parse_shop(self, response):
		headers = response.meta['headers']
		data = response.json()
		city = data['city']
		yield {
			"Producer ID": '',
			"p_id": self.p_id - 1,
			"Producer": f"{self.shop_name} - {city}",
			"Description": '',
			"Link": 'https://www.lyonsroar.ca',
			"SKU": "",
			"City": city,
			"Province": data['province'],
			"Store Name": self.shop_name,
			"Postal Code": data['postal_code'],
			"long": data['long'],
			"lat": data['lat'],
			"ccc": "",
			"Page Url": 'https://www.lyonsroar.ca',
			"Active": "",
			"Main image": 'https://www.lyonsroar.ca/wp-content/uploads/2021/04/lyons-01.jpg',
			"Image 2": "",
			"Image 3": "",
			"Image 4": '',
			"Image 5": '',
			"Type": "",
			"License Type": "",
			"Date Licensed": "",
			"Phone": '(204) 585 2595',
			"Phone 2": "",
			"Contact Name": "",
			"EmailPrivate": "",
			"Email": '',
			"Social": '',
			"FullAddress": "",
			"Address": data['address'],
			"Additional Info": "",
			"Created": "",
			"Comment": "",
			"Updated": ""
		}
		page = 1
		yield scrapy.Request(f'https://app.buddi.io/ropis/menu?page={page}', headers=headers, meta={'headers': headers, 'page': page}, dont_filter=True, callback=self.parse_menu)

	def parse_menu(self, response):
		headers = response.meta['headers']
		page = response.meta['page'] + 1
		data = response.json()['data']
		for product in data:
			yield scrapy.Request(f'https://app.buddi.io/ropis/products/{product["id"]}', headers=headers, callback=self.parse_product, dont_filter=True)
		if data:
			yield scrapy.Request(f'https://app.buddi.io/ropis/menu?page={page}', headers=headers, meta={'headers': headers, 'page': page}, dont_filter=True, callback=self.parse_menu)

	def parse_product(self, response):
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
		try:
			img = data["images"][0]["public_path"]
		except:
			img = ''
		thc_name = ''
		cbd_name = ''
		sym = data["thc_cbd_symbol"]
		thc = main_data["thc"] if main_data["thc"] else data["thc"]
		if thc:
			thc_name = 'THC'
			thc += sym
		else:
			thc = ''
		cbd = main_data["cbd"] if main_data["cbd"] else data["cbd"]
		if cbd:
			cbd_name = 'CBD'
			cbd += sym
		else:
			cbd = ''
		weight = ''
		if data["sizes"][0]["weight"] and data["short_unit"]:
			weight = f'{data["sizes"][0]["weight"]}{data["short_unit"]}'
		yield {
			"Page URL": f"https://www.lyonsroar.ca/products/#/product/{product_id}",
			"Brand": brand,
			"Name": data["name"],
			"SKU": "",
			"Out stock status": in_stock,
			"Stock count": stock_qt,
			"Currency": "CAD",
			"ccc": "",
			"Price": main_data["price"],
			"Manufacturer": self.shop_name,
			"Main image": img,
			"Description": data["description"],
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
			"p_id": self.p_id - 1
		}