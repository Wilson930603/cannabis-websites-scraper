from weedmapsscraper.spiders.base_spider import BaseSpider
import scrapy


class WeedmapsStore(BaseSpider):
	name = 'weedmaps'
	provinces = {
		"AB": "Alberta",
		"BC": "British Columbia",
		"MB": "Manitoba",
		"NB": "New Brunswick",
		"NL": "Newfoundland and Labrador",
		"NS": "Nova Scotia",
		"NT": "Northwest Territories",
		"NU": "Nunavut",
		"ON": "Ontario",
		"PE": "Prince Edward Island",
		"QC": "Québec",
		"SK": "Saskatchewan",
		"YT": "Yukon"
	}

	def __init__(self, city='', province='', **kwargs):
		super().__init__(**kwargs)
		self.city = city.lower().replace("_", " ")
		self.province = province.upper()

	def start_requests(self):
		url = f'https://api-g.weedmaps.com/wm/v1/geocode?query={self.city} {self.province} Canada&types=postcode%2Cplace%2Clocality%2Cneighborhood%2Caddress%2Cpoi&proximity=-114.0575%2C51.04583'
		yield scrapy.Request(url, callback=self.parse_location)

	def parse_location(self, response):
		locations = response.json()["data"]
		for location in locations:
			if location["attributes"]["country"] == 'Canada' and location["attributes"]["city"].lower() == self.city and location["attributes"]['state_abv'] == self.province:
				lat = location["attributes"]["latitude"]
				lon = location["attributes"]["longitude"]
				yield scrapy.Request(f'https://api-g.weedmaps.com/discovery/v2/listings?sort_by=position_distance&filter%5Bamenities%5D%5B%5D=has_ordering_online&filter%5Bbounding_radius%5D=75mi&filter%5Bbounding_latlng%5D={lat}%2C{lon}&latlng={lat}%2C{lon}&page_size=150&include%5B%5D=facets.has_curbside_pickup&include%5B%5D=facets.retailer_services&page=1', callback=self.parse)
				break

	def parse(self, response):
		stores = response.json()['data']['listings']
		for store in stores:
			slug = store['slug']
			p_id = store["id"]
			yield {
				'Producer ID': '',
				'p_id': p_id,
				'Producer': f"{store['name']} - {store['city']}",
				'Description': store['intro_body'].strip().rstrip(),
				'Link': store['web_url'],
				'SKU': '',
				'City': store['city'],
				'Province': store['state'],
				'Store Name': store['name'],
				'Postal Code': store['zip_code'],
				'long': store['longitude'],
				'lat': store['latitude'],
				'ccc': '',
				'Page Url': store['web_url'],
				'Active': '',
				'Main image': store['avatar_image']['original_url'],
				'Image 2': store['avatar_image']['small_url'],
				'Image 3': '',
				'Image 4': '',
				'Image 5': '',
				'Type': store['type'],
				'License Type': store['license_type'],
				'Date Licensed': '',
				'Phone': store['phone_number'],
				'Phone 2': '',
				'Contact Name': '',
				'EmailPrivate': '',
				'Email': store['email'],
				'Social': '',
				'FullAddress': store['address'],
				'Address': '',
				'Additional Info': '',
				'Created': '',
				'Comment': '',
				'Updated': ''
			}
			yield scrapy.Request(f'http://api-g.weedmaps.com/discovery/v1/listings/dispensaries/{slug}/menu_items?page_size=150&page=1', meta={"slug": slug, "p_id": p_id}, callback=self.parse_products)
		if len(stores) >= 150:
			first_part, next_page = response.url.split('&page=')
			next_page = int(next_page) + 1
			yield scrapy.Request(f"{first_part}&page={next_page}", callback=self.parse)

	def parse_products(self, response):
		slug = response.meta['slug']
		p_id = response.meta['p_id']
		products = response.json()['data']['menu_items']
		brands = self.settings.get('BRANDS', [])
		brands_lower = [x.lower() for x in brands]
		if len(products) >= 150:
			first_url, next_page = response.url.split('&page=')
			next_page = int(next_page) + 1
			yield scrapy.Request(f"{first_url}&page={next_page}", callback=self.parse_products, meta={"slug": slug, "p_id": p_id})
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
				"Page URL": f"https://weedmaps.com/dispensaries/{slug}/menu/{product['slug']}",
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
				"p_id": p_id
			}
			yield scrapy.Request(f"http://api-g.weedmaps.com/discovery/v1/listings/dispensaries/{slug}/menu_items/{product['slug']}", meta={'item': item}, callback=self.get_description)

	def get_description(self, response):
		item = response.meta['item']
		description = response.json()["data"]["menu_item"]["body"].strip().rstrip()
		item['Description'] = description
		yield item
