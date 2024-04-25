import scrapy
from Independent.spiders.base_spider import BaseSpider
from websocket import create_connection


class HighLandBudsSpider(BaseSpider):
	name = 'highlandbuds'
	start_urls = ['https://www.highlandbuds.ca/contact']
	shop_name = 'Highland Buds'
	p_id = '25710091'

	def parse(self, response):
		img = response.xpath('//img/@src').get()
		phone = response.xpath('//div[@id="comp-jv4acng7"]/p[2]/span/text()').get().replace('-', ' ')
		email = response.xpath('//div[@id="comp-j6vv22j3"]/p[2]/span/a/text()').get()
		addr, city, pro_zip = response.xpath('//div[@id="comp-j6vv22j1"]/p[2]/span/text()').get().split(', ')
		province, postal_code = pro_zip.split(' ', 1)
		item = {
			"Producer ID": '',
			"p_id": self.p_id,
			"Producer": f"{self.shop_name} - {city}",
			"Description": "",
			"Link": 'https://www.highlandbuds.ca/',
			"SKU": "",
			"City": city,
			"Province": province,
			"Store Name": self.shop_name,
			"Postal Code": postal_code,
			"long": '',
			"lat": '',
			"ccc": "",
			"Page Url": 'https://www.highlandbuds.ca/',
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
		yield scrapy.Request('https://www.highlandbuds.ca/about', meta={'item': item}, callback=self.parse_products)

	def parse_products(self, response):
		item = response.meta['item']
		p = response.xpath('//div[@id="comp-ih0hhpre"]/p//text()').getall()
		desc = p[0] + '\n' + p[2]
		item['Description'] = desc
		yield item
		wss_link = 'wss://s-usc1c-nss-368.firebaseio.com/.ws?v=5&ns=api2-clickspace-tv'
		ws = create_connection(wss_link)
		ws.recv()
		ws.send('{"t":"d","d":{"r":1,"a":"s","b":{"c":{"sdk.js.8-2-6":1}}}}')
		ws.recv()
		ws.send(
			'{"t":"d","d":{"r":2,"a":"q","b":{"p":"greenline/mergedList/ids/1907/1908/ccd3353155246183bf4a35f765c8aa9e","h":""}}}')
		ws.recv()
		result = ws.recv()
		json_data = ''
		while True:
			try:
				json_data = eval(result)
				break
			except:
				result += ws.recv()
		ids = json_data['d']['b']['d']
		nb = 3
		for id_obj in ids:
			obj_oid = ids[id_obj]
			nb += 1
			msg_send = '{{"t":"d","d":{{"r":{},"a":"q","b":{{"p":"/greenline/mergedList/products/1907/1908/ccd3353155246183bf4a35f765c8aa9e/{}","h":""}}}}}}'.format(nb, obj_oid)
			ws.send(msg_send)
			ws.recv()
			res = ws.recv()
			json_response = eval(res.replace('true', 'True').replace('false', 'False'))
			print(res)
			product_init = json_response['d']['b']['d']
			products = []
			if 'variants' in product_init:
				for key in product_init['variants']:
					products.append(product_init['variants'][str(key)])
			else:
				products.append(product_init)
			for prod in products:
				product = prod['partPos']
				try:
					brand = prod['partDb']['brandName']
				except:
					brand = ''
				stock = product['stock']
				status = 'In Stock'
				if not product['inStock']:
					status = 'Out of Stock'
				price = product['currentPriceNum']
				old_price = product['regularPriceNum']
				if price == old_price:
					old_price = ''
				img = ['', '', '', '', '']
				if 'imageUrls' in product:
					images = product['imageUrls']
					ln = len(images)
					for i in range(0, min(ln, 5)):
						img[i] = images[str(i)]
				sku = ''
				if 'sku' in product:
					sku = product['sku']
				thc_name = ''
				thc = ''
				if 'thcMin' in product:
					min_x = product['thcMin']
					max_x = product['thcMax']
					thc_name = 'THC'
					if min_x == max_x:
						thc = f'{max_x}'
					else:
						thc = f'{min_x}-{max_x}'
					if thc == '0':
						thc_name = ''
						thc = ''
					else:
						try:
							thc += f"{prod['partDb']['thcUom']}"
						except:
							thc += "mg"
				cbd_name = ''
				cbd = ''
				if 'cbdMin' in product:
					min_x = product['cbdMin']
					max_x = product['cbdMax']
					cbd_name = 'CBD'
					if min_x == max_x:
						cbd = f'{max_x}'
					else:
						cbd = f'{min_x}-{max_x}'
					if cbd == '0':
						cbd_name = ''
						cbd = ''
					else:
						try:
							cbd += f"{prod['partDb']['cbdUom']}"
						except:
							cbd += "mg"
				try:
					weight = prod['partDb']['netSizeSummary']
				except:
					weight = ''
				desc = ''
				if 'longDescription' in product:
					desc = product['longDescription']
				print(product['id'])
				yield {
					"Page URL": 'https://www.highlandbuds.ca/menu',
					"Brand": brand,
					"Name": product['productName'],
					"SKU": sku,
					"Out stock status": status,
					"Stock count": stock,
					"Currency": "CAD",
					"ccc": "",
					"Price": price,
					"Manufacturer": '',
					"Main image": img[0],
					"Description": desc,
					"Product ID": product['id'],
					"Additional Information": "",
					"Meta description": "",
					"Meta title": "",
					"Old Price": old_price,
					"Equivalency Weights": "",
					"Quantity": '',
					"Weight": weight,
					"Option": "",
					"Option type": "",
					"Option Value": "",
					"Option image": "",
					"Option price prefix": "",
					"Cat tree 1 parent": product['categories']['0'],
					"Cat tree 1 level 1": '',
					"Cat tree 1 level 2": "",
					"Cat tree 2 parent": "",
					"Cat tree 2 level 1": "",
					"Cat tree 2 level 2": "",
					"Cat tree 2 level 3": "",
					"Image 2": img[1],
					"Image 3": img[2],
					"Image 4": img[3],
					"Image 5": img[4],
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
					"p_id": self.p_id
				}
		ws.close()
