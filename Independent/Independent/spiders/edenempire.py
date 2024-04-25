from Independent.spiders.base_spider import BaseSpider
import scrapy


class EdenEmpireSpider(BaseSpider):
	name = 'edenempire'
	shop_name = 'Eden Empire'
	shop_data = [
		{
			'p_id': 18736871,
			'id': 8,
			'url': 'https://myeden.ca/location/garden-city/',
			'province': 'MB',
			'postal_code': 'R2V 3P4'
		},
		{
			'p_id': 18736872,
			'id': 9,
			'url': 'https://myeden.ca/location/vancouver-fraser-street/',
			'province': 'BC',
			'postal_code': 'V5V 4G4'
		}
	]

	def start_requests(self):
		for shop in self.shop_data:
			p_id = shop['p_id']
			id = shop['id']
			url = shop['url']
			province = shop['province']
			postal_code = shop['postal_code']
			yield scrapy.Request(url, callback=self.parse, meta={'p_id': p_id, 'id': id, 'province': province, 'postal_code': postal_code})

	def parse(self, response):
		p_id = response.meta['p_id']
		id = response.meta['id']
		province = response.meta['province']
		postal_code = response.meta['postal_code']
		img = response.xpath('//div[@data-id="29e45ada"]/div/a/img/@src').get()
		phone = response.xpath('//div[@data-id="c675179"]/div/text()').get().strip().rstrip()
		addr, city = response.xpath('//div[@data-id="9871bee"]/div/p/text()').get().rsplit(', ', 1)
		desc = response.xpath('//div[@data-id="5d92baf"]/div/text()').get().strip().rstrip()
		social = '|'.join(response.xpath('//div[@data-id="f8d8e17"]//a/@href').getall())
		yield {
			"Producer ID": '',
			"p_id": p_id,
			"Producer": f"{self.shop_name} - {city}",
			"Description": desc,
			"Link": response.url,
			"SKU": "",
			"City": city,
			"Province": province,
			"Store Name": self.shop_name,
			"Postal Code": postal_code,
			"long": '',
			"lat": '',
			"ccc": "",
			"Page Url": response.url,
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
			"Email": 'info@edenempire.com',
			"Social": social,
			"FullAddress": "",
			"Address": addr,
			"Additional Info": "",
			"Created": "",
			"Comment": "",
			"Updated": ""
		}
		yield scrapy.Request(f'https://dc3q2iaxujzuu.cloudfront.net/index.php/api/getStoreProductVariants?store_id={id}', callback=self.parse_products, meta={'p_id': p_id, 'url': response.url})

	def parse_products(self, response):
		p_id = response.meta['p_id']
		url = response.meta['url']
		data = response.json()['data']
		for category in data:
			for product in category['variants']:
				stock_qt = int(float(product['variant_stock']))
				in_stock = 'In Stock' if stock_qt > 0 else 'Out of Stock'
				if product['isdiscounted']:
					old_price = product['variant_price']
					price = round(float(old_price) * (1 - product['discount_rate']/100), 2)
				else:
					price = product['variant_price']
					old_price = ''
				yield {
					"Page URL": url,
					"Brand": product['brand'],
					"Name": product['product_name'],
					"SKU": "",
					"Out stock status": in_stock,
					"Stock count": stock_qt,
					"Currency": "CAD",
					"ccc": "",
					"Price": price,
					"Manufacturer": self.shop_name,
					"Main image": product['image_url'],
					"Description": product["product_desc"],
					"Product ID": product['product_id'],
					"Additional Information": '',
					"Meta description": "",
					"Meta title": "",
					"Old Price": old_price,
					"Equivalency Weights": '',
					"Quantity": "",
					"Weight": f"{product['dry_weight']}g" if product['dry_weight'] else '',
					"Option": "",
					"Option type": '',
					"Option Value": "",
					"Option image": "",
					"Option price prefix": "",
					"Cat tree 1 parent": product['product_category_name'],
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
					"Attribute 1": "CBD" if product['product_cbd'] else '',
					"Attribute Value 1": product['product_cbd'],
					"Attribute 2": "THC" if product['product_thc'] else '',
					"Attribute value 2": product['product_thc'],
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
