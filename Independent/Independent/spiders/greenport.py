from Independent.spiders.base_spider import BaseSpider
import scrapy


class GreenportScraper(BaseSpider):
	name = 'greenport'
	start_urls = ['https://rpc.lobojane.com:9443/stores/1299.json']
	shop_name = 'GreenPort'
	p_id = '27653001'

	def parse(self, response):
		data = response.json()['data']['attributes']
		city = data['city']
		shop = {
			"Producer ID": '',
			"p_id": self.p_id,
			"Producer": f"{self.shop_name} - {city}",
			"Description": "",
			"Link": data['url'],
			"SKU": "",
			"City": city,
			"Province": data['region'],
			"Store Name": self.shop_name,
			"Postal Code": data['postal_code'],
			"long": data['longitude'],
			"lat": data['latitude'],
			"ccc": "",
			"Page Url": data['url'],
			"Active": "",
			"Main image": 'https://greenport.store/wp-content/uploads/2021/05/greenport-logo-cannabis.png',
			"Image 2": "",
			"Image 3": "",
			"Image 4": '',
			"Image 5": '',
			"Type": "",
			"License Type": "",
			"Date Licensed": "",
			"Phone": data['phone'],
			"Phone 2": "",
			"Contact Name": "",
			"EmailPrivate": "",
			"Email": '',
			"Social": '',
			"FullAddress": "",
			"Address": data['address'],
			"Additional Info": "",
			"Created": "",
			"Comment": "",
			"Updated": ""
		}
		yield scrapy.Request('https://greenport.store/', meta={'shop': shop}, callback=self.parse_additional)

	def parse_additional(self, response):
		shop = response.meta['shop']
		social = '|'.join(response.xpath('//a[@target="_blank"]/@href').getall()[1:])
		shop['Social'] = social
		yield shop
		yield scrapy.Request('https://rpc.lobojane.com:9443/stores/1299/products.json', callback=self.parse_menu)

	def parse_menu(self, response):
		products = response.json()['data']
		for product in products:
			product_id = product['id']
			yield scrapy.Request(f'https://rpc.lobojane.com:9443/products/static/{product_id}.json', callback=self.parse_product, meta={'id': product_id}, dont_filter=True)

	def parse_product(self, response):
		product = response.json()[0]
		product_id = response.meta['id']
		print(product_id)
		images = eval(product['images'])
		img = ['', '', '', '', '']
		for i in range(min(len(images), 5)):
			img[i] = images[i]
		desc = product['description']
		item = {
			"Page URL": f'https://greenport.store/shop-all/?lobo[product]={product_id}&lobo[sid]=1299',
			"Brand": product['producer'],
			"Name": product["name"],
			"SKU": '',
			"Out stock status": '',
			"Stock count": '',
			"Currency": "CAD",
			"ccc": "",
			"Price": '',
			"Manufacturer": self.shop_name,
			"Main image": img[0],
			"Description": desc,
			"Product ID": product_id,
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
			"Cat tree 1 parent": product["type"],
			"Cat tree 1 level 1": '',
			"Cat tree 1 level 2": "",
			"Cat tree 2 parent": '',
			"Cat tree 2 level 1": "",
			"Cat tree 2 level 2": "",
			"Cat tree 2 level 3": "",
			"Image 2": img[1],
			"Image 3": img[2],
			"Image 4": img[3],
			"Image 5": img[4],
			"Sort order": "",
			"Attribute 1": '',
			"Attribute Value 1": '',
			"Attribute 2": '',
			"Attribute value 2": '',
			"Attribute 3": "",
			"Attribute value 3": '',
			"Attribute 4": "",
			"Attribute value 4": "",
			"Reviews": '',
			"Review link": "",
			"Rating": '',
			"Address": '',
			"p_id": self.p_id
		}
		variants = eval(product['variants'])
		nb_variants = len(variants)
		has_variants = nb_variants > 1
		if has_variants:
			item['Option type'] = "Choose an option"
		for variant in variants:
			try:
				weight = variant['quantity']
				if has_variants:
					item['Option Value'] = weight
			except:
				pass
			id_variant = variant['id']
			yield scrapy.Request(f'https://rpc.lobojane.com:9443/products/dynamic/{id_variant}.json?store_id=1299', meta={'product': item, 'variants': has_variants}, callback=self.parse_product_additional)

	def parse_product_additional(self, response):
		item = response.meta['product']
		has_variants = response.meta['variants']
		data = response.json()
		if not data:
			item["Out stock status"] = 'Out of Stock'
			item["Stock count"] = 0
			yield item
		else:
			data = data[0]
			stock = data['stock']
			status = 'In Stock'
			if stock == 0:
				status = 'Out of Stock'
			item["Out stock status"] = status
			item["Stock count"] = stock
			price = data['price']
			old_price = data['original_price']
			if not old_price:
				old_price = ''
			item['Price'] = price
			if has_variants:
				item['Option price prefix'] = price
			item['Old Price'] = old_price
			try:
				cbd_name = ''
				cbd = ''
				cbd_v = eval(data['cbd'])
				if cbd_v[0] != 0.0 and cbd_v[1] != 0.0:
					cbd_name = 'CBD'
					if cbd_v[0] == cbd_v[1]:
						cbd = f'{cbd_v[0]}'
					else:
						cbd = f'{cbd_v[0]}-{cbd_v[1]}'
				item["Attribute 1"] = cbd_name
				item["Attribute Value 1"] = cbd
			except:
				pass
			try:
				thc_name = ''
				thc = ''
				thc_v = eval(data['thc'])
				if thc_v[0] != 0.0 and thc_v[1] != 0.0:
					thc_name = 'THC'
					if thc_v[0] == thc_v[1]:
						thc = f'{thc_v[0]}'
					else:
						thc = f'{thc_v[0]}-{thc_v[1]}'
				item["Attribute 2"] = thc_name
				item["Attribute value 2"] = thc
			except:
				pass
			yield item
