from Independent.spiders.base_spider import BaseSpider
import scrapy


class DeeprivercannabisScraper(BaseSpider):
	name = 'deeprivercannabis'
	shop_name = 'Deep River Cannabis'
	start_urls = ['https://deeprivercannabis.com/contact-us/']
	p_id = '65927083'

	def parse(self, response):
		img = response.xpath('//img[@id="logo"]/@src').get()
		parags = response.xpath('//div[@class="et_pb_text_inner"]/p')
		phone = parags[2].xpath('./text()').get().strip().rstrip()
		addr, city_pro, postal_code = parags[1].xpath('./text()').getall()
		postal_code = postal_code.strip().rstrip()
		city, province = city_pro.strip().split(', ')
		item = {
			"Producer ID": '',
			"p_id": self.p_id,
			"Producer": f"{self.shop_name} - {city}",
			"Description": "",
			"Link": "https://deeprivercannabis.com/",
			"SKU": "",
			"City": city,
			"Province": province,
			"Store Name": self.shop_name,
			"Postal Code": postal_code,
			"long": "",
			"lat": "",
			"ccc": "",
			"Page Url": "https://deeprivercannabis.com/",
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
			"Address": addr,
			"Additional Info": "",
			"Created": "",
			"Comment": "",
			"Updated": ""
		}
		yield scrapy.Request('https://deeprivercannabis.com/contact-us/', meta={'item': item}, callback=self.parse_description)

	def parse_description(self, response):
		desc = '\n'.join(response.xpath('(//div[@class="et_pb_text_inner"])[3]//text()').getall())
		item = response.meta['item']
		item['Description'] = desc
		yield item
		req_params = {"ProductGroupId": "", "SortId": 1, "Page": 1, "PageSize": 1000, "SearchText": "", "Brand": [], "Weight": [], "Species": [], "BranchId": 1, "Terpene": "", "Mood": "", "THCMAX": 100, "THCMIN": 0, "CBDMAX": 100, "CBDMIN": 0, "FromExpressCheckout": False}
		yield scrapy.http.JsonRequest('https://deepriverwebmenu-api.azurewebsites.net/api/products/filterProducts', data=req_params, callback=self.parse_products, headers={"Content-Type": "application/json"}, dont_filter=True)

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
			img_url = 'https://deepriverwebmenu.azurewebsites.net/035c9c51101d29574fbe9c6d9f20eaae.jpg'
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
				"Page URL": f'https://deepriverwebmenu.azurewebsites.net/product/{product["id"]}',
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
				"p_id": self.p_id
			}
