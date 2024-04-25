from Independent.spiders.base_spider import BaseSpider
import scrapy


class Leisure4cScraper(BaseSpider):
	name = 'leisure4c'
	start_urls = ['https://api-g.weedmaps.com/discovery/v1/listings/dispensaries/leisure-for-cannabis/']
	p_id = '2803410'

	def parse(self, response):
		store = response.json()['data']['listing']
		yield {
			'Producer ID': '',
			'p_id': self.p_id,
			'Producer': f"{store['name']} - {store['city']}",
			'Description': store['intro_body'].strip().rstrip(),
			'Link': 'https://leisure4c.wm.store/',
			'SKU': '',
			'City': store['city'],
			'Province': store['state'],
			'Store Name': store['name'],
			'Postal Code': store['zip_code'],
			'long': store['longitude'],
			'lat': store['latitude'],
			'ccc': '',
			'Page Url': 'https://leisure4c.wm.store/',
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
		yield scrapy.Request('https://api-g.weedmaps.com/discovery/v1/listings/dispensaries/leisure-for-cannabis/menu_items?page_size=150&page=1', callback=self.parse_products)

	def parse_products(self, response):
		products = response.json()['data']['menu_items']
		if len(products) >= 150:
			first_url, next_page = response.url.split('&page=')
			next_page = int(next_page) + 1
			yield scrapy.Request(f"{first_url}&page={next_page}", callback=self.parse_products)
		for product in products:
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
			if '-' in brand:
				brand = brand.replace('-', '')
			try:
				product_id = product['brand_endorsement']['product_id']
			except:
				product_id = ''
			item = {
				"Page URL": f"https://leisure4c.wm.store/menu/{product['slug']}",
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
				"Quantity": "",
				"Weight": product["price"]["label"],
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
			yield scrapy.Request(f"http://api-g.weedmaps.com/discovery/v1/listings/dispensaries/leisure-for-cannabis/menu_items/{product['slug']}", meta={'item': item}, callback=self.get_description, headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36"})

	def get_description(self, response):
		item = response.meta['item']
		description = response.json()["data"]["menu_item"]["body"].strip().rstrip()
		item['Description'] = description
		yield item
