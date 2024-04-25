from Independent.spiders.base_spider import BaseSpider
import scrapy


class RiversideScraper(BaseSpider):
	name = 'riversidecannabis'
	start_urls = ['https://www.riversidecannabis.ca/']
	p_id = '8708731'

	def parse(self, response):
		text = response.xpath('//div[@id="comp-isk9y3ew"]//text()').getall()
		phone = text[0]
		email = text[2]
		address, city_pro = text[6].rstrip().split('. ')
		city, province = city_pro.split(', ')
		postal_code = text[8]
		desc = '\n'.join(response.xpath('//div[@id="comp-k36qxb4b__item-j9r6lf43"]//text()').getall())
		img = "https://static.wixstatic.com/media/afbceb_5b170cf82c244b67b83b673906ed4985~mv2.png/v1/crop/x_73,y_77,w_639,h_639/fill/w_134,h_134,al_c,q_85,usm_0.66_1.00_0.01/AaaLogo.webp"
		yield {
			"Producer ID": '',
			"p_id": self.p_id,
			"Producer": f"Riverside Cannabis - {city}",
			"Description": desc,
			"Link": "https://www.riversidecannabis.ca/",
			"SKU": "",
			"City": city,
			"Province": province,
			"Store Name": "Riverside Cannabis",
			"Postal Code": postal_code,
			"long": "",
			"lat": "",
			"ccc": "",
			"Page Url": "https://www.riversidecannabis.ca/",
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
			"EmailPrivate": email,
			"Email": '',
			"Social": '',
			"FullAddress": "",
			"Address": address,
			"Additional Info": "",
			"Created": "",
			"Comment": "",
			"Updated": ""
		}
		req_params = {"ProductGroupId": "", "SortId": 1, "Page": 1, "PageSize": 1000, "SearchText": "", "Brand": [], "Weight": [], "Species": [], "BranchId": 1, "Terpene": "", "Mood": "", "THCMAX": 100, "THCMIN": 0, "CBDMAX": 100, "CBDMIN": 0, "FromExpressCheckout": False}
		yield scrapy.http.JsonRequest('https://riversidewebmenu-api.azurewebsites.net/api/products/filterProducts', data=req_params, callback=self.parse_products,  headers={"Content-Type": "application/json"}, dont_filter=True)

	def parse_products(self, response):
		products = response.json()["data"]["products"]
		for product in products:
			brand = product['brand']
			if not brand:
				brand = product['name'].split(' - ')[0]
			if '-' not in product["name"]:
				brand = ""
			brand = brand.replace('-', '')
			qt = int(product["quantity"])
			status = "In Stock"
			if qt == 0:
				status = "Out of Stock"
			img_url = 'https://riversidewebmenu.azurewebsites.net/035c9c51101d29574fbe9c6d9f20eaae.jpg'
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
			name = product["name"]
			yield {
				"Page URL": f'https://riversidewebmenu.azurewebsites.net/product/{product["id"]}',
				"Brand": brand,
				"Name": name,
				"SKU": product["sku"],
				"Out stock status": status,
				"Stock count": qt,
				"Currency": "CAD",
				"ccc": "",
				"Price": price,
				"Manufacturer": 'Riverside Cannabis',
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

