from Independent.spiders.base_spider import BaseSpider
import scrapy


class RoyalcannabissupplyScraper(BaseSpider):
	name = 'royalcannabissupply'
	shop_name = 'Royal Cannabis Supply Co.'
	p_id = '17620091'
	start_urls = ['https://api-g.weedmaps.com/discovery/v1/search?q=%20Royal%20Cannabis%20Supply%20Company&latlng=43.74523%2C-79.63225&filter%5Btypes%5D%5B%5D=category&filter%5Btypes%5D%5B%5D=listing&filter%5Btypes%5D%5B%5D=brand&filter%5Btypes%5D%5B%5D=tag&filter%5Btypes%5D%5B%5D=strain&filter%5Bbounding_radius%5D=30mi&page_size=1']

	def parse(self, response):
		store = response.json()['data']['results'][0]['attributes']
		slug = store['slug']
		yield {
			'Producer ID': '',
			'p_id': self.p_id,
			'Producer': f"{self.shop_name} - {store['city']}",
			'Description': store['intro_body'].strip().rstrip(),
			'Link': 'https://www.royalcannabissupply.com/menu',
			'SKU': '',
			'City': store['city'],
			'Province': store['state'],
			'Store Name': self.shop_name,
			'Postal Code': store['zip_code'],
			'long': store['longitude'],
			'lat': store['latitude'],
			'ccc': '',
			'Page Url': 'https://www.royalcannabissupply.com/menu',
			'Active': '',
			'Main image': store['avatar_image']['original_url'],
			'Image 2': store['avatar_image']['small_url'],
			'Image 3': '',
			'Image 4': '',
			'Image 5': '',
			'Type': store['type'],
			'License Type': store['license_type'],
			'Date Licensed': '',
			'Phone': store['phone_number'].replace('-', ' '),
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
		yield scrapy.Request(f'http://api-g.weedmaps.com/discovery/v1/listings/dispensaries/{slug}/menu_items?page_size=150&page=1', meta={"slug": slug}, callback=self.parse_products)

	def parse_products(self, response):
		slug = response.meta['slug']
		products = response.json()['data']['menu_items']
		if len(products) >= 150:
			first_url, next_page = response.url.split('&page=')
			next_page = int(next_page) + 1
			yield scrapy.Request(f"{first_url}&page={next_page}", callback=self.parse_products, meta={"slug": slug})
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
			try:
				product_id = product['brand_endorsement']['product_id']
			except:
				product_id = ''
			if price == old_price:
				old_price = ''
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
				"p_id": self.p_id
			}
			yield scrapy.Request(
				f"http://api-g.weedmaps.com/discovery/v1/listings/dispensaries/{slug}/menu_items/{product['slug']}",
				meta={'item': item}, callback=self.get_description)

	def get_description(self, response):
		item = response.meta['item']
		description = response.json()["data"]["menu_item"]["body"].strip().rstrip()
		item['Description'] = description
		yield item
