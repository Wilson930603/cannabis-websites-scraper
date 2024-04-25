from Independent.spiders.base_spider import BaseSpider
import scrapy


class MissjonescannabisScraper(BaseSpider):
	name = 'missjonescannabis'
	base_pid = 187537690
	headers = {
		'api-token': 'b09172c4e50751f49bf00180aa0cd3b7b24d3f0e',
		'auth-token': 'b13b98c95f73e1443c9eab88609ef6047144a5b1'
	}
	headers2 = {
		'app-id': 'yq6jaKsPfIUmXkPSKy8n7T4W8QhIjKsL',
		'app-secret': 'QyEeMOYw9VoysVM9UkHIO4nzGmywYJgT'
	}
	shop_name = 'Miss Jones'

	def start_requests(self):
		yield scrapy.Request('https://locations-service.api.unoapp.io/clients/businesses/f03251d1-ba69-4d0c-a1de-c2e0f734c48e/locations/search/nearby?lat=36.706911&long=4.2333355&radius=500000&operation_hours=false&address=true&contact_details=true&settings=false&images=true&delivery_hours=false&timeslots=false', headers=self.headers, callback=self.parse)

	def parse(self, response):
		shops = response.json()["payload"]
		i = 0
		for data in shops:
			p_id = self.base_pid + i
			link = f'https://budler.ca/miss-jones/{data["slug"]}'
			address = data['address']
			addr = address['address_line_1']
			city = address['city']
			postal_code = address['postal_code']
			lat = address['latitude']
			long = address['longitude']
			province = address['timezone_id'].split('/')[1]
			img = data['images'][0]['image_url']
			phone = ''
			email = ''
			for contact in data['contact_details']:
				if contact['name'] == 'phone':
					phone = contact['value']
				elif contact['name'] == 'email':
					email = contact['value']
			yield {
				"Producer ID": '',
				"p_id": p_id,
				"Producer": f"{self.shop_name} - {city}",
				"Description": "",
				"Link": link,
				"SKU": "",
				"City": city,
				"Province": province,
				"Store Name": self.shop_name,
				"Postal Code": postal_code,
				"long": long,
				"lat": lat,
				"ccc": "",
				"Page Url": link,
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
				"Social": '',
				"FullAddress": "",
				"Address": addr,
				"Additional Info": "",
				"Created": "",
				"Comment": "",
				"Updated": ""
			}
			location_id = data['id']
			yield scrapy.Request(f'https://cannabis-products-api.prod.unoapp.io/api/v1/locationCategories/{location_id}/location?include_products=1&include_brands=1&include_variants=1&include_cannabis_attributes=1&include_thc_cbd=1&include_location_product_category=1&featured_categories=0', headers=self.headers2, callback=self.parse_products, meta={'p_id': p_id, 'link': link})
			i += 1

	def parse_products(self, response):
		p_id = response.meta['p_id']
		link = response.meta['link']
		categories = response.json()['payload']
		for category in categories:
			cat_name = category['name']
			products = category['products']
			for product in products:
				brand = product['brand']['name']
				thc_name = ''
				thc = ''
				cbd_name = ''
				cbd = ''
				thc_cbd = product['thc_cbd_levels']
				try:
					unit = thc_cbd['concentration_unit']
				except:
					unit = ''
				try:
					cbd_min = thc_cbd['cbd_min']
					cbd_max = thc_cbd['cbd_max']
					if cbd_min == 0 and cbd_max == 0:
						pass
					else:
						cbd_name = 'CBD'
						if cbd_min == cbd_max:
							cbd = f'{cbd_min}{unit}'
						else:
							cbd = f'{cbd_min} - {cbd_max}{unit}'
				except:
					pass
				try:
					thc_min = thc_cbd['thc_min']
					thc_max = thc_cbd['thc_max']
					if thc_min == 0 and thc_max == 0:
						pass
					else:
						thc_name = 'THC'
						if thc_min == thc_max:
							thc = f'{thc_min}{unit}'
						else:
							thc = f'{thc_min} - {thc_max}{unit}'
				except:
					pass
				item = {
					"Page URL": link,
					"Brand": brand,
					"Name": product['name'],
					"SKU": product['sku'],
					"Out stock status": '',
					"Stock count": '',
					"Currency": "CAD",
					"ccc": "",
					"Price": '',
					"Manufacturer": self.shop_name,
					"Main image": product['image'],
					"Description": product['description'],
					"Product ID": '',
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
					"Cat tree 1 parent": cat_name,
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
					"p_id": p_id
				}
				has_variants = len(product['variants']) > 1
				if has_variants:
					item["Option type"] = "Choose a size"
				for variant in product['variants']:
					price = variant['sale_price']
					old_price = variant['price']
					if price == old_price:
						old_price = ''
					weight = variant['size']
					status = 'Out of Stock'
					if variant['available']:
						status = 'In Stock'
					qte = variant['no_of_units']
					item["Out stock status"] = status
					item["Stock count"] = qte
					item['Price'] = price
					item['Old Price'] = old_price
					item['Weight'] = weight
					if has_variants:
						item['Option price prefix'] = price
						item['Option Value'] = weight
					yield item
