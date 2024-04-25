from Independent.spiders.base_spider import BaseSpider
import scrapy


class WonderpotScraper(BaseSpider):
	name = 'wonderpot'
	start_urls = ['https://wonderpot.ca/']
	shop_data = [
		{
			'p_id': '278386101',
			'id': 1,
			'link': 'https://wonderpot.ca/stores/bloor/'
		},
		{
			'p_id': '278386102',
			'id': 2,
			'link': 'https://wonderpot.ca/stores/eglinton/'
		}
	]
	shop_name = 'Wonder Pot'

	def parse(self, response):
		img = response.xpath('//img[@class="custom-logo"]/@src').get()
		desc = '\n'.join(response.xpath('//div[@data-id="fd73139"]//h5//text()').getall())
		social = '|'.join(response.xpath('//div[@class="footer-social-inner-wrap element-social-inner-wrap social-show-label-false ast-social-color-type-custom ast-social-element-style-filled"]/a/@href').getall())
		for shop in self.shop_data:
			p_id = shop['p_id']
			shop_id = shop['id']
			link = shop['link']
			yield scrapy.Request(link, meta={'p_id': p_id, 'shop_id': shop_id, 'i': img, 'd': desc, 's': social}, callback=self.parse_shop)

	def parse_shop(self, response):
		p_id = response.meta['p_id']
		shop_id = response.meta['shop_id']
		img = response.meta['i']
		desc = response.meta['d']
		social = response.meta['s']
		contact = response.xpath('(//div[@class="elementor-widget-container"])[5]')
		if shop_id == 1:
			details = contact.xpath('./h5/text()').getall()
			email = details[3]
			addr = details[0][0:-1]
			city, province = details[1].split(', ')
			postal_code = details[2]
		else:
			email = contact[0].xpath('./h5/text()').get()
			address = contact[0].xpath('./h4/text()').getall()
			addr = address[0][0:-1]
			city, province = address[1].split(', ')
			postal_code = address[2]
		yield {
			"Producer ID": '',
			"p_id": p_id,
			"Producer": f"{self.shop_name} - {city}",
			"Description": desc,
			"Link": response.url,
			"SKU": "",
			"City": city,
			"Province": province,
			"Store Name": self.shop_name,
			"Postal Code": postal_code,
			"long": '',
			"lat": '',
			"ccc": "",
			"Page Url": response.url,
			"Active": "",
			"Main image": img,
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
			"Email": email,
			"Social": social,
			"FullAddress": "",
			"Address": addr,
			"Additional Info": "",
			"Created": "",
			"Comment": "",
			"Updated": ""
		}
		req_params = {"ProductGroupId": "", "SortId": 1, "Page": 1, "PageSize": 1000, "SearchText": "", "Brand": [], "Weight": [], "Species": [], "BranchId": shop_id, "Terpene": "", "Mood": "", "THCMAX": 100, "THCMIN": 0, "CBDMAX": 100, "CBDMIN": 0, "FromExpressCheckout": False}
		yield scrapy.http.JsonRequest('https://wonderpotwebmenu-api.azurewebsites.net/api/products/filterProducts', data=req_params, callback=self.parse_products, headers={"Content-Type": "application/json"}, dont_filter=True, meta={'p_id': p_id})

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
			img_url = 'https://wonderpotwebmenu.azurewebsites.net/035c9c51101d29574fbe9c6d9f20eaae.jpg'
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
			old_price = product["price"]["price"]
			price = product["price"]["discountedPrice"]
			if old_price == price:
				old_price = ''
			yield {
				"Page URL": 'https://wonderpot.ca/shoppingcart/',
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
