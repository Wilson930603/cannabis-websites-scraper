from Independent.spiders.base_spider import BaseSpider
import scrapy


class TbContarioSpider(BaseSpider):
	name = 'tbcontario'
	start_urls = ['https://www.tbcontario.com/about-us']
	shops = [
		{
			'site': 'https://www.tbcontario.com/tastebudswestonroad',
			'id': '1c5c84fc-d770-4434-8797-a86827b9aea1'
		},
		{
			'site': 'https://www.tbcontario.com/copy-of-north-york-weston',
			'id': '64b7face-7b48-4156-9382-906f5caea29c'
		}
	]
	shop_name = 'Taste Buds Cannabis'

	def parse(self, response):
		description = ' '.join(response.xpath('//div[@id="comp-kqr6ljfi"]/p//text()').getall())
		for shop in self.shops:
			yield scrapy.Request(f'https://www.superanytime.com/api/store?storeId={shop["id"]}', meta={'link': shop["site"], 'desc': description}, dont_filter=True, callback=self.parse_shop)

	def parse_shop(self, response):
		data = response.json()
		p_id = data["sellerId"]
		link = response.meta["link"]
		description = response.meta["desc"]
		city = data["town"]

		yield {
			"Producer ID": '',
			"p_id": f'801257{p_id}',
			"Producer": f"{self.shop_name} - {city}",
			"Description": description,
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
			"Social": 'https://www.instagram.com/tbc.ontario/',
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
			description = product["description"]
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
				"Description": description,
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
				"p_id": f'801257{p_id}'
			}
