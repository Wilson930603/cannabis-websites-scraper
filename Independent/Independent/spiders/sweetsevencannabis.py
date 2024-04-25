from Independent.spiders.base_spider import BaseSpider
import scrapy


class SweetsevercannabisScraper(BaseSpider):
	name = 'sweetsevencannabis'
	start_urls = ['https://www.sweetsevencannabis.ca/locations/']
	shop_name = 'Sweet Seven Cannabis Co.'
	base_pid = 42975631

	def parse(self, response):
		email = response.xpath('//a[@title="Email Us"]/text()').get()
		social_links = response.xpath('//ul[@class="menu-topbar-social centered"]/li/a/@href').getall()
		social = f'{social_links[0]}|{social_links[2]}'
		img = response.xpath('//img[@class="logo"]/@src').get()
		cards = response.xpath('//div[@class="col-md-3"]')
		ids = [1, 1, 3, 4]
		for i in range(0, 4):
			p_id = self.base_pid + i
			card = cards[i]
			link = card.xpath('./p/a[1]/@href').get()
			lat, long = card.xpath('./a/@href').get().split('@')[1].split(',')
			contact = card.xpath('./ul/li/text()').getall()
			addr = contact[0]
			city, province, postal_code = contact[1].split(', ')
			phone = contact[2].replace('-', ' ')
			yield {
				"Producer ID": '',
				"p_id": p_id,
				"Producer": f"{self.shop_name} - {city}",
				"Description": '',
				"Link": link,
				"SKU": "",
				"City": city,
				"Province": province,
				"Store Name": self.shop_name,
				"Postal Code": postal_code,
				"long": long,
				"lat": lat,
				"ccc": "",
				"Page Url": link,
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
				"Social": social,
				"FullAddress": "",
				"Address": addr,
				"Additional Info": "",
				"Created": "",
				"Comment": "",
				"Updated": ""
			}
			req_params = {"ProductGroupId": "", "SortId": 1, "Page": 1, "PageSize": 1000, "SearchText": "", "Brand": [], "Weight": [], "Species": [], "BranchId": ids[i], "Terpene": "", "Mood": "", "THCMAX": 100, "THCMIN": 0, "CBDMAX": 100, "CBDMIN": 0, "FromExpressCheckout": False}
			yield scrapy.http.JsonRequest( 'https://sweetsevenwebmenu-api.azurewebsites.net/api/products/filterProducts', data=req_params, callback=self.parse_products, headers={"Content-Type": "application/json"}, dont_filter=True, meta={'p_id': p_id, 'link': link})

	def parse_products(self, response):
		p_id = response.meta['p_id']
		link = response.meta['link']
		products = response.json()["data"]["products"]
		for product in products:
			brand = product['brand']
			if not brand:
				brand = product['name'].split(' - ')[0]
			qt = int(product["quantity"])
			status = "In Stock"
			if qt == 0:
				status = "Out of Stock"
			img_url = 'https://sweetsevenwebmenu.azurewebsites.net/035c9c51101d29574fbe9c6d9f20eaae.jpg'
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
				"Page URL": f'{link}all',
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
