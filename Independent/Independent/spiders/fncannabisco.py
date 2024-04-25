from Independent.spiders.base_spider import BaseSpider
import scrapy


class FnCannabisCoSpider(BaseSpider):
	name = 'fncannabisco'
	shop_name = 'FN Cannabis CO'
	start_urls = ['https://www.superanytime.com/api/store?storeId=b4895ed1-fdac-4d4f-b239-9a123fe432a0']
	p_id = 18528013

	def parse(self, response):
		data = response.json()
		city = data["town"]
		yield {
			"Producer ID": '',
			"p_id": self.p_id,
			"Producer": f"{self.shop_name} - {city}",
			"Description": "",
			"Link": 'https://www.fncannabisco.ca/',
			"SKU": "",
			"City": city,
			"Province": data["state"],
			"Store Name": self.shop_name,
			"Postal Code": data['postalCode'],
			"long": data["longitude"],
			"lat": data["latitude"],
			"ccc": "",
			"Page Url": 'https://www.fncannabisco.ca/',
			"Active": "",
			"Main image": data['logoUrl'],
			"Image 2": "",
			"Image 3": "",
			"Image 4": '',
			"Image 5": '',
			"Type": "",
			"License Type": "",
			"Date Licensed": "",
			"Phone": "",
			"Phone 2": "",
			"Contact Name": "",
			"EmailPrivate": "",
			"Email": "",
			"Social": '',
			"FullAddress": "",
			"Address": data["address"],
			"Additional Info": "",
			"Created": "",
			"Comment": "",
			"Updated": ""
		}
		yield scrapy.Request('https://www.superanytime.com/api/search?storeId=b4895ed1-fdac-4d4f-b239-9a123fe432a0&query=&category=&offset=0&minPrice=0&maxPrice=2147483647&limit=10000', callback=self.parse_products)

	def parse_products(self, response):
		products = response.json()["products"]
		for product in products:
			brand = product["maker"]
			thc = product["thc"]
			thc_name = 'THC'
			if not thc or thc == '0.0':
				thc_name = ''
				thc = ''
			cbd = product["cbd"]
			cbd_name = 'CBD'
			if not cbd or cbd == '0.0':
				cbd_name = ''
				cbd = ''
			stock = 'In Stock'
			if product["outOfStock"]:
				stock = 'Out of Stock'
			price = float(product["price"]) / 100
			old_price = product["compareAtPrice"]
			if old_price:
				old_price = float(old_price) / 100
			else:
				old_price = ''
			desc = product["description"]
			if not desc:
				desc = ''
			yield {
				"Page URL": 'https://www.fncannabisco.ca/shop-now',
				"Brand": brand,
				"Name": product["title"],
				"SKU": "",
				"Out stock status": stock,
				"Stock count": product["quantity"],
				"Currency": "CAD",
				"ccc": "",
				"Price": price,
				"Manufacturer": self.shop_name,
				"Main image": product["imageURL"],
				"Description": desc,
				"Product ID": "",
				"Additional Information": '',
				"Meta description": "",
				"Meta title": "",
				"Old Price": old_price,
				"Equivalency Weights": '',
				"Quantity": "",
				"Weight": product["container"],
				"Option": "",
				"Option type": '',
				"Option Value": "",
				"Option image": "",
				"Option price prefix": "",
				"Cat tree 1 parent": product["style"],
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
				"Reviews": "",
				"Review link": "",
				"Rating": '',
				"Address": '',
				"p_id": self.p_id
			}
