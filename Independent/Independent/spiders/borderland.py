from Independent.spiders.base_spider import BaseSpider
from websocket import create_connection


class BorderlandScraper(BaseSpider):
	name = 'borderland'
	shop_name = 'Borderland Cannabis'
	p_id = '238116'
	start_urls = ['https://borderland.budguide.io/#/main']

	def parse(self, response):
		yield {
			"Producer ID": '',
			"p_id": self.p_id,
			"Producer": f"{self.shop_name}",
			"Description": "",
			"Link": 'https://borderland.budguide.io/#/main',
			"SKU": "",
			"City": '',
			"Province": '',
			"Store Name": self.shop_name,
			"Postal Code": '',
			"long": '',
			"lat": '',
			"ccc": "",
			"Page Url": 'https://borderland.budguide.io/#/main',
			"Active": "",
			"Main image": '',
			"Image 2": "",
			"Image 3": "",
			"Image 4": '',
			"Image 5": '',
			"Type": "",
			"License Type": "",
			"Date Licensed": "",
			"Phone": '',
			"Phone 2": "",
			"Contact Name": "",
			"EmailPrivate": "",
			"Email": '',
			"Social": '',
			"FullAddress": "",
			"Address": '',
			"Additional Info": "",
			"Created": "",
			"Comment": "",
			"Updated": ""
		}
		wss_link = 'wss://s-usc1c-nss-370.firebaseio.com/.ws?v=5&ns=api2-clickspace-tv'
		ws = create_connection(wss_link)
		ws.recv()
		ws.send('{"t":"d","d":{"r":1,"a":"s","b":{"c":{"sdk.js.8-2-6":1}}}}')
		ws.recv()
		ws.send('{"t":"d","d":{"r":2,"a":"q","b":{"p":"/iqmetrix/mergedList/ids/BorderlandCannabis-dot-Budvue/238116/0fe2c2cb91d4585f6352d0f0af774a75","h":""}}}')
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
			msg_send = '{{"t":"d","d":{{"r":{},"a":"q","b":{{"p":"/iqmetrix/mergedList/products/BorderlandCannabis-dot-Budvue/238116/0fe2c2cb91d4585f6352d0f0af774a75/{}","h":""}}}}}}'.format(
				nb, obj_oid)
			ws.send(msg_send)
			ws.recv()
			res = ws.recv()
			if str(res) == '2':
				res = ws.recv()
				res += ws.recv()
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
				brand = ''
				if 'brandName' in product:
					brand = product['brandName']
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
					"Page URL": 'https://borderland.budguide.io/#/main',
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
