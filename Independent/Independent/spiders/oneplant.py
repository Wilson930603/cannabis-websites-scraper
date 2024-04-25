import re

from Independent.spiders.base_spider import BaseSpider
import scrapy
import requests as r


class OneplantScraper(BaseSpider):
	name = 'oneplant'
	headers = {
		'waio-company': '22',
		'authorization': 'Bearer F33BBAC54C479761F72EE2379ED0F4120F7FFBBCF65CDCB021'
	}

	location_data = {}
	basic_p_id = 58724360
	shop_name = 'One Plant'

	def start_requests(self):
		yield scrapy.Request('https://www.oneplant.ca/stores/', headers={'cookie': 'age_gate=1; popup=true'})

	def parse(self, response):
		self.shop_urls = response.xpath('//a[@class="location-content-btn"]/@href').getall()
		res = r.get('https://menuapi.waiosoft.com/locations', headers=self.headers)
		locations = res.json()['body']['locations']
		for location in locations:
			location_id = str(location['locationid'])
			self.location_data[location_id] = location
		for url in self.shop_urls:
			p_id = self.basic_p_id
			self.basic_p_id += 1
			yield scrapy.Request(url, callback=self.parse_shop, dont_filter=True, meta={'p_id': p_id})

	def parse_shop(self, response):
		shop_link = response.url
		print(shop_link)
		p_id = response.meta['p_id']
		location_id = response.xpath('//script[@id="waiomenuloader"]/@data-location').get()
		location_data = self.location_data[location_id]
		try:
			addr, city, province, postal_code = location_data['storeaddress'].split(', ')
		except:
			try:
				addr, city, pro_zip = location_data['storeaddress'].split(', ')
				province, postal_code = pro_zip.split(' ', 1)
			except:
				if ',' in location_data['storeaddress']:
					full_addr, pro_zip = location_data['storeaddress'].split(', ')
					province, postal_code = pro_zip.split(' ', 1)
					addr, city = full_addr.rsplit(' ', 1)
				elif ' ON ' in location_data['storeaddress']:
					addr, city, province, postal_code = location_data['storeaddress'].rsplit(' ', 3)
				else:
					addr, city = location_data['storeaddress'].rsplit(' ', 1)
					province = ''
					postal_code = ''
		yield {
			"Producer ID": '',
			"p_id": p_id,
			"Producer": f"{self.shop_name} - {location_data['storename']}",
			"Description": "",
			"Link": shop_link,
			"SKU": "",
			"City": city,
			"Province": province,
			"Store Name": self.shop_name,
			"Postal Code": postal_code,
			"long": location_data['storelong'],
			"lat": location_data['storelat'],
			"ccc": "",
			"Page Url": shop_link,
			"Active": "",
			"Main image": location_data['brandurl'],
			"Image 2": "",
			"Image 3": "",
			"Image 4": '',
			"Image 5": '',
			"Type": "",
			"License Type": "",
			"Date Licensed": "",
			"Phone": location_data['storephone'],
			"Phone 2": "",
			"Contact Name": "",
			"EmailPrivate": "",
			"Email": "",
			"Social": "",
			"FullAddress": "",
			"Address": addr,
			"Additional Info": "",
			"Created": "",
			"Comment": "",
			"Updated": ""
		}
		headers = self.headers
		headers['waio-location'] = location_id
		yield scrapy.Request(f'https://menuapi.waiosoft.com/location/{location_id}/products', dont_filter=True, callback=self.parse_menu, headers=headers, meta={'shop_id': location_id, 'p_id': p_id, 'shop_link': shop_link})

	def parse_menu(self, response):
		shop_id = response.meta['shop_id']
		shop_link = response.meta['shop_link']
		p_id = response.meta['p_id']
		products = response.json()['body']['products']
		headers = self.headers
		headers['waio-location'] = shop_id
		for product in products:
			yield scrapy.Request(f'https://menuapi.waiosoft.com/location/{shop_id}/products/{product["productId"]}', headers=headers, callback=self.parse_product, meta={'p_id': p_id, 'shop_link': shop_link})

	def parse_product(self, response):
		shop_link = response.meta['shop_link']
		p_id = response.meta['p_id']
		product = response.json()['body']
		product_id = product['productId']
		print(f'{p_id} --> {product_id}')
		images = ['', '', '', '', '']
		nb_images = len(product['images'])
		for i in range(min(nb_images, 5)):
			images[i] = product['images'][i]
		thc = ''
		cbd = ''
		thc_name = ''
		cbd_name = ''
		if 'thccbddisplay' in product:
			measure = product['thccbddisplay']
			if 'cbd' in product:
				cbd = f'{product["cbd"]}{measure}'
				cbd_name = 'CBD'
			if 'thc' in product:
				thc = f'{product["thc"]}{measure}'
				thc_name = 'THC'
		desc = product["description"]
		if desc:
			cleanr = re.compile('<.*?>')
			desc = re.sub(cleanr, '', desc)
		else:
			desc = ''
		item = {
			"Page URL": f'{shop_link}#/products/{product_id}',
			"Brand": product["brandname"],
			"Name": product["productName"],
			"SKU": "",
			"Out stock status": '',
			"Stock count": '',
			"Currency": "CAD",
			"ccc": "",
			"Price": '',
			"Manufacturer": self.shop_name,
			"Main image": images[0],
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
			"Cat tree 1 parent": product["category"],
			"Cat tree 1 level 1": "",
			"Cat tree 1 level 2": "",
			"Cat tree 2 parent": '',
			"Cat tree 2 level 1": "",
			"Cat tree 2 level 2": "",
			"Cat tree 2 level 3": "",
			"Image 2": images[1],
			"Image 3": images[2],
			"Image 4": images[3],
			"Image 5": images[4],
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
			"p_id": p_id
		}
		nb_variations = len(product['variations'])
		if nb_variations > 1:
			item['Option type'] = "Choose an option"
		for variation in product['variations']:
			stock = variation['quantityStatus']
			if stock == 'Out Of Srock':
				stock = 'Out of Stock'
			else:
				stock = 'In Stock'
			price = variation['price']
			old_price = ''
			if variation['onsale'] == '1':
				old_price = variation['originalPrice']
			weight = variation['displayname']
			item['Out stock status'] = stock
			item['Price'] = price
			item['Old Price'] = old_price
			item['Weight'] = weight
			if nb_variations > 1:
				item['Option Value'] = weight
				item['Option price prefix'] = price
			yield item
