from Independent.spiders.base_spider import BaseSpider
import scrapy


class GreencloudwebmenuScraper(BaseSpider):
	name = 'greencloudwebmenu'
	start_urls = ['https://thegreencloudcannabis.com/about-us/']
	shop_name = 'The Green Cloud Cannabis'
	base_pid = 140179890

	def parse(self, response):
		desc = response.xpath('//p[@class="has-text-align-center has-text-color has-custom-font has-custom-lineheight has-custom-letterspacing"]/text()').get()
		social = '|'.join(response.xpath('//div[@class="wp-block-coblocks-social wp-block-coblocks-social-profiles has-colors"]/ul/li/a/@href').getall())
		email = response.xpath('//h2[@class="has-text-align-center"]/text()').get()
		img = response.xpath('//img[@class="custom-logo"]/@src').get()
		contact = response.xpath('//article[@id="post-59"]/div/h2[@class="has-text-align-center" or @class="has-text-align-center has-text-color"]//text()').getall()
		addresses = [contact[0], contact[2], contact[4], contact[6]]
		phones = [contact[1], contact[3], contact[5], contact[7]]
		for i in range(1, 5):
			p_id = self.base_pid + i
			address = addresses[i-1].replace(', Canada', '').replace(' Canada', '')
			phone = phones[i-1].replace('-', ' ')
			if i != 2:
				addr, city, province = address.split(', ')
			else:
				addr, province = address.rsplit(', ', 1)
				addr, city = addr.rsplit(' ', 1)
			item = {
				"Producer ID": '',
				"p_id": p_id,
				"Producer": f"{self.shop_name} - {city}",
				"Description": desc,
				"Link": 'https://greencloudwebmenu.azurewebsites.net/',
				"SKU": "",
				"City": city,
				"Province": province,
				"Store Name": self.shop_name,
				"Postal Code": "",
				"long": '',
				"lat": '',
				"ccc": "",
				"Page Url": 'https://greencloudwebmenu.azurewebsites.net/',
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
			yield item
			req_params = {"ProductGroupId": "", "SortId": 1, "Page": 1, "PageSize": 1000, "SearchText": "", "Brand": [], "Weight": [], "Species": [], "BranchId": i, "Terpene": "", "Mood": "", "THCMAX": 100, "THCMIN": 0, "CBDMAX": 100, "CBDMIN": 0, "FromExpressCheckout": False}
			yield scrapy.http.JsonRequest('https://greencloudwebmenu-api.azurewebsites.net/api/products/filterProducts', data=req_params, callback=self.parse_products, headers={"Content-Type": "application/json"}, dont_filter=True, meta={'p_id': p_id})

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
			img_url = 'https://greencloudwebmenu.azurewebsites.net/035c9c51101d29574fbe9c6d9f20eaae.jpg'
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
				"Page URL": f'https://greencloudwebmenu.azurewebsites.net/product/{product["id"]}',
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
