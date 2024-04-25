from Independent.spiders.base_spider import BaseSpider
import scrapy


class UpInSkySpider(BaseSpider):
	name = 'upinsky'
	shop_name = 'Up In Sky'
	p_id = 67454012
	start_urls = ['https://upinsky.ca/']

	def parse(self, response):
		yield {
			"Producer ID": '',
			"p_id": self.p_id,
			"Producer": f"{self.shop_name} - Winnipeg",
			"Description": '',
			"Link": "https://upinsky.ca/",
			"SKU": "",
			"City": "Winnipeg",
			"Province": "MB",
			"Store Name": self.shop_name,
			"Postal Code": "R2M3W8",
			"long": "",
			"lat": "",
			"ccc": "",
			"Page Url": "https://upinsky.ca/",
			"Active": "",
			"Main image": "https://upinsky.ca/php/upload/logo/60dab2b489af0.jpeg",
			"Image 2": '',
			"Image 3": '',
			"Image 4": '',
			"Image 5": '',
			"Type": "",
			"License Type": "",
			"Date Licensed": "",
			"Phone": "(204) 306 0369",
			"Phone 2": "",
			"Contact Name": "",
			"EmailPrivate": "",
			"Email": "info@upinsky.ca",
			"Social": "https://www.facebook.com/upinsmoke|https://plus.google.com/upinsmoke|https://www.instagram.com/upinsmokehenderson/",
			"FullAddress": "",
			"Address": "1615 St Mary's Rd Unit 102",
			"Additional Info": "",
			"Created": "",
			"Comment": "",
			"Updated": ""
		}
		yield scrapy.Request('https://upinsky.ca/php/view-front-categories.php', callback=self.parse_category)

	def parse_category(self, response):
		for category in response.json():
			yield scrapy.Request(f'https://upinsky.ca/php/view-front-subcategories.php?category_id={category["id"]}', callback=self.parse_sub_category)

	def parse_sub_category(self, response):
		for sub_category in response.json():
			yield scrapy.Request(f'https://upinsky.ca/php/view-products-front.php?product-subcategory={sub_category["slug"]}', callback=self.parse_products)

	def parse_products(self, response):
		for product in response.json()['data']:
			yield scrapy.Request(f'https://upinsky.ca/php/view-products.php?product-details={product["md_id"]}-{product["slug"]}', callback=self.parse_product)

	def parse_product(self, response):
		print(response.url)
		product = response.json()["data"][0]
		brand = product["brand_name"]
		try:
			weight = f'{product["size"]} {product["measure"]}'
			if not product["size"]:
				weight = ''
		except:
			weight = ''
		old_price = product["previous_price"]
		if old_price == "0" or old_price == product["price"]:
			old_price = ''
		status = 'In Stock'
		if not product["stock"]:
			status = 'Out Of Stock'
		cannabis = product['cannabis_per_size']
		if cannabis == "0":
			cannabis = ''
		cbd = ''
		thc = ''
		if product['cbd_min'] == "0" and product['cbd_max'] == "0":
			pass
		else:
			cbd = f"{product['cbd_min']}-{product['cbd_max']}mg/g"
		if product['thc_min'] == "0" and product['thc_max'] == "0":
			pass
		else:
			thc = f"{product['thc_min']}-{product['thc_max']}mg/g"
		item = {
			"Page URL": f'https://upinsky.ca/product/product-details/{product["md_id"]}-{product["slug"]}',
			"Brand": brand,
			"Name": product["name"],
			"SKU": product["sku"],
			"Out stock status": status,
			"Stock count": "",
			"Currency": "CAD",
			"ccc": "",
			"Price": product["default_currency_price_tax"],
			"Manufacturer": self.shop_name,
			"Main image": f'https://upinsky.ca/php/upload/products/{product["photo"]}',
			"Description": product["short_description"],
			"Product ID": product["id"],
			"Additional Information": '',
			"Meta description": "",
			"Meta title": "",
			"Old Price": old_price,
			"Equivalency Weights": f"{cannabis}g of Cannabis",
			"Quantity": "",
			"Weight": weight,
			"Option": "",
			"Option type": '',
			"Option Value": "",
			"Option image": "",
			"Option price prefix": "",
			"Cat tree 1 parent": product["categories_name"],
			"Cat tree 1 level 1": '',
			"Cat tree 1 level 2": "",
			"Cat tree 2 parent": product["subcategories_name"],
			"Cat tree 2 level 1": "",
			"Cat tree 2 level 2": "",
			"Cat tree 2 level 3": "",
			"Image 2": '',
			"Image 3": '',
			"Image 4": '',
			"Image 5": '',
			"Sort order": "",
			"Attribute 1": "CBD",
			"Attribute Value 1": cbd,
			"Attribute 2": "THC",
			"Attribute value 2": thc,
			"Attribute 3": "",
			"Attribute value 3": "",
			"Attribute 4": "",
			"Attribute value 4": "",
			"Reviews": '',
			"Review link": "",
			"Rating": '',
			"Address": '',
			"p_id": self.p_id
		}
		yield scrapy.Request(f'https://upinsky.ca/php/view-total-ratings.php?product-details={product["md_id"]}-{product["slug"]}', callback=self.parse_rating, meta={'item': item, 'size': product['size'], 'measure': product['measure'], 'price': product['size_price_converted_tax'], 'cann': product['cannabis_per_size']})

	def parse_rating(self, response):
		rating = response.json()["data"][0]
		item = response.meta["item"]
		item["Reviews"] = rating['totalRating']
		if item["Reviews"] == "0":
			item["Rating"] = ''
		else:
			item["Rating"] = rating['avgRate']
		sizes = response.meta["size"].split(',')
		measure = response.meta["measure"]
		prices = response.meta["price"].split(',')
		cannabis = response.meta["cann"].split(',')
		if len(sizes) > 1:
			for size, price, cann in zip(sizes, prices, cannabis):
				item["Option type"] = "Choose a Size"
				item["Option Value"] = f"{size}{measure}"
				item["Option price prefix"] = price
				item["Equivalency Weights"] = f"{cann}g of Cannabis"
				yield item
		else:
			yield item
