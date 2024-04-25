from Independent.spiders.base_spider import BaseSpider
import scrapy


class GoodCookieCannabisScraper(BaseSpider):
	name = 'goodcookiecannabis'
	start_urls = []
	shop_name = 'Good Cookie'
	p_ids = ['3904', '3939']
	headers = {
		'authority': 'goodcookiecannabis.com',
		'pragma': 'no-cache',
		'cache-control': 'no-cache',
		'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
		'sec-ch-ua-mobile': '?0',
		'upgrade-insecure-requests': '1',
		'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36',
		'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
		'sec-fetch-site': 'same-origin',
		'sec-fetch-mode': 'navigate',
		'sec-fetch-user': '?1',
		'sec-fetch-dest': 'document',
		'accept-language': 'en-US,en;q=0.9,fr-FR;q=0.8,fr;q=0.7',
	}

	def start_requests(self):
		yield scrapy.Request('https://goodcookiecannabis.com/', headers=self.headers, callback=self.parse)

	def parse(self, response):
		contact = response.xpath('//footer[@class="container s-8-mt"]/div/div[1]/div')
		cont = contact[2].xpath('./a/text()').getall()
		self.phone = cont[0].strip().rstrip()
		self.email = cont[1].strip().rstrip()
		for p_id in self.p_ids:
			yield scrapy.Request(f'https://app.buddi.io/ropis/stores/{p_id}/get-token', callback=self.parse_token, meta={'p_id': p_id})

	def parse_token(self, response):
		p_id = response.meta['p_id']
		token = response.json()['token']
		headers = {
			'authority': 'app.buddi.io',
			'authorization-domain': 'https://goodcookiecannabis.com',
			'authorization': f'Bearer {token}'
		}
		yield scrapy.Request('https://app.buddi.io/ropis/auth/me', headers=headers, callback=self.parse_shop, meta={'p_id': p_id, 'headers': headers}, dont_filter=True)

	def parse_shop(self, response):
		p_id = response.meta['p_id']
		headers = response.meta['headers']
		data = response.json()
		lat = data['lat']
		long = data['long']
		yield {
			"Producer ID": '',
			"p_id": p_id,
			"Producer": f"{self.shop_name} - {data['name']}",
			"Description": '',
			"Link": f'https://goodcookiecannabis.com/?store_id={p_id}#/menu',
			"SKU": "",
			"City": data['city'],
			"Province": data['province'],
			"Store Name": self.shop_name,
			"Postal Code": data['postal_code'],
			"long": long,
			"lat": lat,
			"ccc": "",
			"Page Url": f'https://goodcookiecannabis.com/?store_id={p_id}#/menu',
			"Active": "",
			"Main image": '',
			"Image 2": "",
			"Image 3": "",
			"Image 4": '',
			"Image 5": '',
			"Type": "",
			"License Type": "",
			"Date Licensed": "",
			"Phone": self.phone,
			"Phone 2": "",
			"Contact Name": "",
			"EmailPrivate": "",
			"Email": self.email,
			"Social": '',
			"FullAddress": "",
			"Address": data['address'],
			"Additional Info": "",
			"Created": "",
			"Comment": "",
			"Updated": ""
		}
		page = 1
		yield scrapy.Request(f'https://app.buddi.io/ropis/menu?page={page}', headers=headers, meta={'p_id': p_id, 'headers': headers, 'page': page}, dont_filter=True, callback=self.parse_menu)

	def parse_menu(self, response):
		p_id = response.meta['p_id']
		headers = response.meta['headers']
		page = response.meta['page'] + 1
		data = response.json()['data']
		for product in data:
			yield scrapy.Request(f'https://app.buddi.io/ropis/products/{product["id"]}', headers=headers, meta={'p_id': p_id}, callback=self.parse_product, dont_filter=True)
		if data:
			yield scrapy.Request(f'https://app.buddi.io/ropis/menu?page={page}', headers=headers, meta={'p_id': p_id, 'headers': headers, 'page': page}, dont_filter=True,  callback=self.parse_menu)

	def parse_product(self, response):
		p_id = response.meta['p_id']
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
			"Page URL": f"https://goodcookiecannabis.com/?store_id={p_id}#/product/{product_id}",
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
			"p_id": p_id
		}
