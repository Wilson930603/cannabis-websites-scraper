from Independent.spiders.base_spider import BaseSpider
import scrapy


class Cannabisjacks(BaseSpider):
	name = 'cannabisjacks'
	start_urls = ['https://www.cannabisjacks.ca/']
	shops = [
		{
			'site': 'https://www.cannabisjacks.ca/shop-north-bay',
			'id': 'ff2d0f24-4002-4eeb-b2e1-ee652c7abb19'
		},
		{
			'site': 'https://www.cannabisjacks.ca/order-timmins',
			'id': '5684dce5-2d4b-40d0-baf8-9721a8277933'
		},
		{
			'site': 'https://www.cannabisjacks.ca/shop-sudbury',
			'id': 'c88efe69-188e-4ef8-a43a-e642777a9452'
		},
		{
			'site': 'https://www.cannabisjacks.ca/shop-sault-ste-marie',
			'id': '5f9297ae-3edb-493d-a01f-c17cae8a0483'
		}
	]
	shop_name = 'Cannabis Jacks'
	social = ''

	def parse(self, response):
		self.social = "|".join(response.xpath('//nav[@class="sqs-svg-icon--list"]/a/@href').getall())
		for shop in self.shops:
			yield scrapy.Request(f'https://www.superanytime.com/api/store?storeId={shop["id"]}', meta={'link': shop["site"]}, dont_filter=True, callback=self.parse_shop)

	def parse_shop(self, response):
		data = response.json()
		p_id = data["sellerId"]
		link = response.meta["link"]
		city = data["town"]

		yield {
			"Producer ID": '',
			"p_id": p_id,
			"Producer": f"{self.shop_name} - {city}",
			"Description": "",
			"Link": link,
			"SKU": "",
			"City": city,
			"Province": data["state"],
			"Store Name": self.shop_name,
			"Postal Code": data['postalCode'],
			"long": data["longitude"],
			"lat": data["latitude"],
			"ccc": "",
			"Page Url": link,
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
			"Social": self.social,
			"FullAddress": "",
			"Address": data["address"],
			"Additional Info": "",
			"Created": "",
			"Comment": "",
			"Updated": ""
		}
		yield scrapy.Request(f'https://www.superanytime.com/api/search?storeId={data["id"]}&query=&category=&offset=0&minPrice=0&maxPrice=2147483647&limit=10000', dont_filter=True, callback=self.parse_products, meta={'p_id': p_id, 'link': link})

	def parse_products(self, response):
		p_id = response.meta['p_id']
		link = response.meta["link"]
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
			yield {
				"Page URL": link,
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
				"Description": product["description"],
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
				"p_id": p_id
			}