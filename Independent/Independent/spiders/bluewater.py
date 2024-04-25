from Independent.spiders.base_spider import BaseSpider
import scrapy


class BluewaterScraper(BaseSpider):
	name = 'bluewater'
	branches = [{'id': 1, 'city': "Oliver", 'p_id': "80735878"}, {'id': 2, 'city': "Penticton", 'p_id': '40639028'}]
	start_urls = ['https://www.bluewatercanna.ca/about-2/']

	def parse(self, response):
		desc = response.xpath('//div[@class="fusion-text fusion-text-1"]/p/text()').get()
		contact = response.xpath('//ul[@class="fusion-checklist fusion-checklist-1 fusion-no-small-visibility fusion-no-medium-visibility"]/li/div/p[1]/text()').getall()
		img = response.xpath('//img[@class="fusion-sticky-logo"]/@src').get()
		address, city = contact[0].strip().split(", ")
		phone = contact[1]
		email = contact[2]
		data_shops = [[desc, address, 'V0H 1T0'], ["", "130 Nanaimo Ave W #101", "V2A 8G1"]]
		for data_shop, branch in zip(data_shops, self.branches):
			city = branch["city"]
			p_id = branch["city"]
			branch_id = branch["id"]
			yield {
				"Producer ID": '',
				"p_id": p_id,
				"Producer": f"Bluewater Cannabis - {city}",
				"Description": data_shop[0],
				"Link": "https://www.bluewatercanna.ca/",
				"SKU": "",
				"City": city,
				"Province": "BC",
				"Store Name": "Bluewater Cannabis",
				"Postal Code": data_shop[2],
				"long": "",
				"lat": "",
				"ccc": "",
				"Page Url": "https://www.bluewatercanna.ca/",
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
				"Address": data_shop[1],
				"Additional Info": "",
				"Created": "",
				"Comment": "",
				"Updated": ""
			}
			req_params = {"ProductGroupId": "", "SortId": 1, "Page": 1, "PageSize": 1000, "SearchText": "", "Brand": [], "Weight": [], "Species": [], "BranchId": branch_id, "Terpene": "", "Mood": "", "THCMAX": 100, "THCMIN": 0, "CBDMAX": 100, "CBDMIN": 0, "FromExpressCheckout": False}
			yield scrapy.http.JsonRequest('https://bluewaterwebmenu-api.azurewebsites.net/api/products/filterProducts', data=req_params, callback=self.parse_products, headers={"Content-Type": "application/json"}, dont_filter=True, meta={"p_id": p_id})

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
			img_url = 'https://bluewaterwebmenu.azurewebsites.net/035c9c51101d29574fbe9c6d9f20eaae.jpg'
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
				cbd = f'{cbd}%'
			else:
				cbd = ''
				cbd_name = ''
			if thc:
				thc = f'{thc}%'
			else:
				thc = ''
				thc_name = ''
			price = product["price"]["price"]
			discounted_price = product["price"]["discountedPrice"]
			if price == discounted_price:
				discounted_price = ''
			yield {
				"Page URL": f'https://bluewaterwebmenu.azurewebsites.net/product/{product["id"]}',
				"Brand": brand,
				"Name": product["name"],
				"SKU": product["sku"],
				"Out stock status": status,
				"Stock count": qt,
				"Currency": "CAD",
				"ccc": "",
				"Price": price,
				"Manufacturer": 'Bluewater Cannabis',
				"Main image": img_url,
				"Description": desc,
				"Product ID": product["id"],
				"Additional Information": '',
				"Meta description": "",
				"Meta title": "",
				"Old Price": discounted_price,
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
