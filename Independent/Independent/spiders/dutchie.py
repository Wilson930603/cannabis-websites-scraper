from Independent.spiders.base_spider import BaseSpider
import scrapy
import requests as r


class DutchieIndependentSpider(BaseSpider):
	name = 'dutchie'
	hashes = None
	start_urls = [
		'https://dutchie.com/dispensary/the-highway-stop',
		'https://dutchie.com/dispensary/the-bakery',
		'https://dutchie.com/dispensary/the-bakery-albert-street'
	]

	def start_requests(self):
		res = r.get('http://localhost:1240/get')
		self.hashes = res.json()
		for url in self.start_urls:
			c_name = url.strip('/').split('/')[-1]
			query_url = f'https://dutchie.com/graphql?operationName=ConsumerDispensaries&variables={{"dispensaryFilter":{{"cNameOrID":"{c_name}"}}}}&extensions={{"persistedQuery":{{"version":1,"sha256Hash":"{self.hashes["DispensaryHash"]}"}}}}'
			yield scrapy.Request(query_url, callback=self.parse)

	def parse(self, response):
		data = response.json()['data']['filteredDispensaries'][0]
		dispensary_id = data['id']
		location = data['location']
		shop_name = data['name']
		postal_code = data['address'].split(', ')[-2].split(' ', 1)[1]
		yield {
			"Producer ID": '',
			"p_id": dispensary_id,
			"Producer": shop_name,
			"Description": data['description'],
			"Link": f'https://dutchie.com/dispensary/{data["cName"]}',
			"SKU": "",
			"City": location['city'],
			"Province": location['state'],
			"Store Name": shop_name,
			"Postal Code": postal_code,
			"long": location['geometry']['coordinates'][0],
			"lat": location['geometry']['coordinates'][1],
			"ccc": "",
			"Page Url": f'https://dutchie.com/dispensary/{data["cName"]}',
			"Active": "",
			"Main image": data['listImage'],
			"Image 2": "",
			"Image 3": "",
			"Image 4": '',
			"Image 5": '',
			"Type": "",
			"License Type": "",
			"Date Licensed": "",
			"Phone": data['phone'] if data['phone'] else '',
			"Phone 2": "",
			"Contact Name": "",
			"EmailPrivate": "",
			"Email": data['email'] if data['email'] else '',
			"Social": '',
			"FullAddress": data['address'],
			"Address": location['ln1'],
			"Additional Info": "",
			"Created": "",
			"Comment": "",
			"Updated": ""
		}
		query_url = f'https://dutchie.com/graphql?operationName=FilteredProducts&variables={{"includeTerpenes":true,"includeCannabinoids":true,"showAllSpecialProducts":true,"productsFilter":{{"dispensaryId":"{dispensary_id}","useCache":false,"sortDirection":1,"sortBy":null}},"page":0,"perPage":10000}}&extensions={{"persistedQuery":{{"version":1,"sha256Hash":"{self.hashes["ProductHashWithDetails"]}"}}}}'
		page_url = f'https://dutchie.com/dispensary/{data["cName"]}/product/'

		yield scrapy.Request(query_url, callback=self.parse_menu, meta={'page_url': page_url})

	def parse_menu(self, response):
		page_url = response.meta['page_url']
		products = response.json()['data']['filteredProducts']['products']
		for product in products:
			qty = product["POSMetaData"]["children"][0]["quantityAvailable"]
			if product['recSpecialPrices']:
				price = product['recSpecialPrices'][0]
				old_price = product["Prices"][0]
			else:
				price = product["Prices"][0]
				old_price = ''
			thc_name = ''
			thc = ''
			cbd_name = ''
			cbd = ''
			if product['THCContent'] and product['THCContent']['range']:
				unit = product['THCContent']['unit']
				if unit == 'PERCENTAGE':
					unit = '%'
				thc = f"{product['THCContent']['range'][0]}{unit}"
				thc_name = 'THC'
			if product['CBDContent'] and product['CBDContent']['range']:
				unit = product['CBDContent']['unit']
				if unit == 'PERCENTAGE':
					unit = '%'
				elif unit == 'MILLIGRAMS':
					unit = 'mg'
				cbd = f"{product['CBDContent']['range'][0]}{unit}"
				cbd_name = 'CBD'
			yield {
				"Page URL": f'{page_url}{product["id"]}',
				"Brand": product["brandName"],
				"Name": product["Name"],
				"SKU": "",
				"Out stock status": 'In Stock' if qty > 0 else 'Out of Stock',
				"Stock count": qty,
				"Currency": "CAD",
				"ccc": "",
				"Price": price,
				"Manufacturer": 'Dutchie',
				"Main image": product["Image"],
				"Description": product["description"],
				"Product ID": product["id"],
				"Additional Information": '',
				"Meta description": "",
				"Meta title": "",
				"Old Price": old_price,
				"Equivalency Weights": product["Options"][0],
				"Quantity": "",
				"Weight": "",
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
				"Attribute 1": cbd_name,
				"Attribute Value 1": cbd,
				"Attribute 2": thc_name,
				"Attribute value 2": thc,
				"Attribute 3": "",
				"Attribute value 3": '',
				"Attribute 4": "",
				"Attribute value 4": "",
				"Reviews": "",
				"Review link": "",
				"Rating": "",
				"Address": '',
				"p_id": product['DispensaryID']
			}
