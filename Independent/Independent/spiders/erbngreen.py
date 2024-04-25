import json

from Independent.spiders.base_spider import BaseSpider
import scrapy
import re
from Independent.spiders import api_parameters
import copy


class ErbngreenScraper(BaseSpider):
	name = 'erbngreen'
	start_urls = []
	shop_name = 'ERBN Green'
	api_parameters = {}

	def start_requests(self):
		params = api_parameters.get_parameters(self.settings.get('PROXY_URL'))
		if params:
			self.api_parameters = params
		yield scrapy.Request('https://erbngreen.com/locations/', callback=self.parse)

	def parse(self, response):
		img = response.xpath('//img[@class="logo-dark"]/@src').get()
		social = '|'.join(response.xpath('//ul[@id="menu-secondary-menu"]/li/a/@href').getall())

		shop_path = re.findall("'store_link' : .+", response.text)[0:3]
		phones = re.findall("'phoneFormatted': .+", response.text)[0:3]
		emails = re.findall("'email': .+", response.text)[0:3]
		addrs = re.findall("'address': .+", response.text)[0:3]
		postal_codes = re.findall("'postalCode': .+", response.text)[0:3]
		cities = re.findall("'city': .+", response.text)[0:3]
		provinces = re.findall("'state': .+", response.text)[0:3]
		coordinates = re.findall("'coordinates': .+", response.text)[0:3]

		p_ids = ['538725376', '538725377', '538725378']
		c_names = ['erbn-green-yongelawrence', 'ebrn-green-dundas', 'rbn-green-picton']
		shop_ids = ['60b80658e5c66900d0092b82', '60b7ce9fac6c3000cbd51581', '60b910b43da19f00a63ee50b']
		for path, p_id, c_name, phone, email, addr, postal_code, city, province, coordinate, shop_id in zip(shop_path, p_ids, c_names, phones, emails, addrs, postal_codes, cities, provinces, coordinates, shop_ids):
			path = path.split('/', 1)[1][0:-2]
			phone = phone.split(": '", 1)[1][0:-2]
			email = email.split(": '", 1)[1][0:-2]
			addr = addr.split(": '", 1)[1][0:-2]
			postal_code = postal_code.split(": '", 1)[1][0:-2]
			city = city.split(": '", 1)[1][0:-2]
			province = province.split(": '", 1)[1][0:-2]
			long, lat = coordinate.split(': [')[1][0:-1].split(', ')
			url = f'https://erbngreen.com/{path}/'
			yield {
				"Producer ID": '',
				"p_id": p_id,
				"Producer": f"{self.shop_name} - {city}",
				"Description": "",
				"Link": url,
				"SKU": "",
				"City": city,
				"Province": province,
				"Store Name": self.shop_name,
				"Postal Code": postal_code,
				"long": long,
				"lat": lat,
				"ccc": "",
				"Page Url": url,
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
				"Email": email,
				"Social": social,
				"FullAddress": "",
				"Address": addr,
				"Additional Info": "",
				"Created": "",
				"Comment": "",
				"Updated": ""
			}
			header = copy.copy(self.api_parameters['search_products_headers'])
			url = self.api_parameters['search_products_url'].format(shop_id)
			yield scrapy.Request(url, headers=header, callback=self.parse_menu, meta={'p_id': p_id, 'path': path}, dont_filter=True)

	def parse_menu(self, response):
		p_id = response.meta['p_id']
		path = response.meta['path']
		try:
			product_data = response.json()
			if "data" in product_data:
				headers = copy.copy(self.api_parameters['search_details_headers'])
				for product in product_data["data"]["filteredProducts"]["products"]:
					if product['recSpecialPrices']:
						price = product['recSpecialPrices'][0]
						old_price = product["Prices"][0]
					else:
						price = product["Prices"][0]
						old_price = ''
					qte = int(product["POSMetaData"]["children"][0]["quantityAvailable"])
					status = 'Out of Stock'
					if qte > 0:
						status = 'In Stock'
					item = {
						"Page URL": f"https://erbngreen.com/{path}/?dtche[product]={product['cName']}",
						"Brand": product["brandName"],
						"Name": product["Name"],
						"SKU": '',
						"Out stock status": status,
						"Stock count": qte,
						"Currency": "CAD",
						"ccc": "",
						"Price": price,
						"Manufacturer": self.shop_name,
						"Main image": product["Image"],
						"Description": '',
						"Product ID": product['id'],
						"Additional Information": '',
						"Meta description": "",
						"Meta title": "",
						"Old Price": old_price,
						"Equivalency Weights": product["Options"][0],
						"Quantity": "",
						"Weight": '',
						"Option": "",
						"Option type": '',
						"Option Value": "",
						"Option image": "",
						"Option price prefix": "",
						"Cat tree 1 parent": product["type"],
						"Cat tree 1 level 1": product["subcategory"] if product["subcategory"] else '',
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
						"Attribute 1": 'THC',
						"Attribute Value 1": [],
						"Attribute 2": '',
						"Attribute value 2": [],
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
					if product["THCContent"]:
						if product["THCContent"]["range"]:
							for THC in product["THCContent"]["range"]:
								if THC:
									item["Attribute Value 1"].append(str(THC))
					item["Attribute Value 1"] = ' - '.join(item["Attribute Value 1"])
					item["Attribute 2"] = 'CBD'
					item["Attribute value 2"] = []
					if product["CBDContent"]:
						if product["CBDContent"]["range"]:
							for CBD in product["CBDContent"]["range"]:
								if CBD:
									item["Attribute value 2"].append(str(CBD))
					item["Attribute value 2"] = ' - '.join(item["Attribute value 2"])
					item["Attribute 3"] = 'Type'
					item["Attribute value 3"] = product["type"]
					item["Attribute 4"] = ''
					item["Attribute value 4"] = ''
					item["Reviews"] = ''
					item["Review link"] = ''
					item["Rating"] = ''
					url = self.api_parameters['search_details_url'].format(item["Product ID"])
					# headers["url"] = f"{Page_Url}/menu/{product['cName']}"
					yield scrapy.Request(url=url, headers=headers, callback=self.parse_products, meta={'item': item})
		except Exception as e:
			self.logger.error(e)

	def parse_products(self, response):
		try:
			item = response.meta["item"]
			data = response.json()
			product = data["data"]["filteredProducts"]["products"][0]
			Additional_Information = json.dumps(product["effects"]) if 'effects' in product else None
			item["Description"] = product["description"]
			try:
				item["Meta description"] = product["brand"]["description"]
			except:
				item["Meta description"] = ""
			item["Additional Information"] = Additional_Information
			yield item
		except Exception as e:
			self.logger.error(response.text)
