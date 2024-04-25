from Independent.spiders.base_spider import BaseSpider
import scrapy


class AthenawebmenuScraper(BaseSpider):
	name = 'athenawebmenu'
	start_urls = ['https://athenawebmenu-api.azurewebsites.net/api/web/home/getStoreRules/1']
	p_id = "25839471"

	def parse(self, response):
		data = response.json()["data"][0]
		addr_related = data["webStoreRulesContent"][0]["content"].rstrip()
		name, full_addr = addr_related.split(' - ')
		addr, city, postal_code = full_addr.split(', ')
		contact_related = data["webStoreRulesContent"][3]["content"]
		email, phone = contact_related.split(' | ')
		email = email.split(' - ')[1].rstrip()
		phone = phone.split(' - ')[1]
		yield {
			"Producer ID": '',
			"p_id": self.p_id,
			"Producer": f"{name} - {city}",
			"Description": '',
			"Link": "https://athenawebmenu.azurewebsites.net/",
			"SKU": "",
			"City": city,
			"Province": "Ontario",
			"Store Name": name,
			"Postal Code": postal_code,
			"long": "",
			"lat": "",
			"ccc": "",
			"Page Url": "https://athenawebmenu.azurewebsites.net/",
			"Active": "",
			"Main image": '',
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
		req_params = {"ProductGroupId": "", "SortId": 1, "Page": 1, "PageSize": 1000, "SearchText": "", "Brand": [], "Weight": [], "Species": [], "BranchId": 1, "Terpene": "", "Mood": "", "THCMAX": 100, "THCMIN": 0, "CBDMAX": 100, "CBDMIN": 0, "FromExpressCheckout": False}
		yield scrapy.http.JsonRequest('https://athenawebmenu-api.azurewebsites.net/api/products/filterProducts', data=req_params, callback=self.parse_products, headers={"Content-Type": "application/json"}, dont_filter=True)

	def parse_products(self, response):
		products = response.json()["data"]["products"]
		for product in products:
			brand = product['brand']
			if not brand:
				brand = product['name'].split(' - ')[0]
			qt = int(product["quantity"])
			status = "In Stock"
			if qt == 0:
				status = "Out of Stock"
			img_url = 'https://athenawebmenu.azurewebsites.net/035c9c51101d29574fbe9c6d9f20eaae.jpg'
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
				"Page URL": f'https://athenawebmenu.azurewebsites.net/product/{product["id"]}',
				"Brand": brand,
				"Name": product["name"],
				"SKU": product["sku"],
				"Out stock status": status,
				"Stock count": qt,
				"Currency": "CAD",
				"ccc": "",
				"Price": price,
				"Manufacturer": 'Athena Cannabis',
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
				"p_id": self.p_id
			}
