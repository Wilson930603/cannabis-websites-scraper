from Independent.spiders.base_spider import BaseSpider
import scrapy


class FlowertowncannabisScraper(BaseSpider):
	name = 'flowertowncannabis'
	start_urls = ['https://flowertowncannabis.ca/contact-us/']
	shop_data = {
		'Bridgenorth': [1, '34882673', 'K0L 1H0'],
		'Beaverton': [2, '53876245', 'L0K 1A0']
	}
	shop_name = 'Flower Town Cannabis'

	def parse(self, response):
		locations = response.xpath('(//div[@class="et_pb_promo_description"])[2]/div/h2/text()').getall()
		phones = response.xpath('(//div[@class="et_pb_promo_description"])[2]/div/p/text()[2]').getall()
		img = response.xpath('//img[@id="logo"]/@src').get()
		for location, phone in zip(locations, phones):
			city, addr = location.rstrip().split(' ', 1)
			phone = phone.split('at ')[1].split(' We')[0][:-2]
			extra = self.shop_data[city]
			id_shop = extra[0]
			p_id_shop = extra[1]
			item = {
				"Producer ID": '',
				"p_id": p_id_shop,
				"Producer": f"{self.shop_name} - {city}",
				"Description": "",
				"Link": f"https://flowertowncannabis.ca/{city.lower()}/",
				"SKU": "",
				"City": city,
				"Province": 'ON',
				"Store Name": self.shop_name,
				"Postal Code": extra[2],
				"long": "",
				"lat": "",
				"ccc": "",
				"Page Url": f"https://flowertowncannabis.ca/{city.lower()}/",
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
				"Email": "",
				"Social": "",
				"FullAddress": "",
				"Address": addr[2:],
				"Additional Info": "",
				"Created": "",
				"Comment": "",
				"Updated": ""
			}
			yield scrapy.Request('https://flowertowncannabis.ca/about-us/', callback=self.parse_description, dont_filter=True, meta={'shop_id': id_shop, 'p_id': p_id_shop, 'item': item})

	def parse_description(self, response):
		item = response.meta['item']
		p_id = response.meta['p_id']
		shop_id = response.meta['shop_id']
		desc = '\n'.join(response.xpath('(//div[@class="et_pb_promo_description"])[2]/div/p/text()').getall())
		item['Description'] = desc
		yield item
		req_params = {"ProductGroupId": "", "SortId": 1, "Page": 1, "PageSize": 1000, "SearchText": "", "Brand": [], "Weight": [], "Species": [], "BranchId": shop_id, "Terpene": "", "Mood": "", "THCMAX": 100, "THCMIN": 0, "CBDMAX": 100, "CBDMIN": 0, "FromExpressCheckout": False}
		yield scrapy.http.JsonRequest('https://flowertownwebmenu-api.azurewebsites.net/api/products/filterProducts', data=req_params, callback=self.parse_products, headers={"Content-Type": "application/json"}, dont_filter=True, meta={'p_id': p_id})

	def parse_products(self, response):
		p_id = response.meta['p_id']
		products = response.json()["data"]["products"]
		for product in products:
			brand = product['brand']
			if not brand:
				brand = product['name'].split(' - ')[0]
			qt = int(product["quantity"])
			status = "In Stock"
			if qt == 0:
				status = "Out of Stock"
			img_url = 'https://flowertownwebmenu.azurewebsites.net/035c9c51101d29574fbe9c6d9f20eaae.jpg'
			if product["imagesUrls"]:
				img_url = product["imagesUrls"][0]
			desc = product['description']
			if not desc:
				desc = ''
			cbd = product['cbD_LEVEL']
			cbd_name = 'CBD'
			thc = product['thC_LEVEL']
			thc_name = 'THC'
			weight = product["weightPerUnit"]
			if weight > 0:
				weight = f'{weight}g'
			else:
				weight = ''
			if cbd:
				cbd = f'{cbd}mg/ml'
			else:
				cbd = ''
				cbd_name = ''
			if thc:
				thc = f'{thc}mg/ml'
			else:
				thc = ''
				thc_name = ''
			price = product["price"]["price"]
			discounted_price = product["price"]["discountedPrice"]
			old_price = ''
			if price == discounted_price:
				discounted_price = ''
			if discounted_price:
				old_price = price
				price = discounted_price
			yield {
				"Page URL": f'https://flowertownwebmenu.azurewebsites.net/product/{product["id"]}',
				"Brand": brand,
				"Name": product["name"],
				"SKU": product["sku"],
				"Out stock status": status,
				"Stock count": qt,
				"Currency": "CAD",
				"ccc": "",
				"Price": price,
				"Manufacturer": self.shop_name,
				"Main image": img_url,
				"Description": desc,
				"Product ID": product["id"],
				"Additional Information": '',
				"Meta description": "",
				"Meta title": "",
				"Old Price": old_price,
				"Equivalency Weights": '',
				"Quantity": "",
				"Weight": weight,
				"Option": "",
				"Option type": '',
				"Option Value": "",
				"Option image": "",
				"Option price prefix": "",
				"Cat tree 1 parent": product["category"],
				"Cat tree 1 level 1": '',
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

