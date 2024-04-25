from Independent.spiders.base_spider import BaseSpider
import scrapy


class UpinsmokeSpider(BaseSpider):
	name = 'highmountain'
	start_urls = ['https://highmountaincannabisinc.com/']

	def parse(self, response):
		header = response.xpath('//div[@class="et_pb_column et_pb_column_4_4 et_pb_column_0  et_pb_css_mix_blend_mode_passthrough et-last-child"]')
		img = header.xpath('.//img/@src').get()
		addr, phone = header.xpath('./div[2]//p/text()').getall()
		line_addr, city, province = addr.split(', ')
		phone = phone.split(' ', 1)[1]
		desc = response.xpath('//div[contains(@class, "et_pb_bg_layout_dark et_pb_media_alignment_center")]//p/text()').getall()[0:6]
		desc = ' '.join(desc)
		yield {
			"Producer ID": '',
			"p_id": "45830864",
			"Producer": f"High Mountain Cannabis - {city}",
			"Description": desc,
			"Link": "https://highmountaincannabisinc.com/",
			"SKU": "",
			"City": city,
			"Province": province,
			"Store Name": "High Mountain Cannabis Inc.",
			"Postal Code": "",
			"long": "",
			"lat": "",
			"ccc": "",
			"Page Url": "https://highmountaincannabisinc.com/",
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
			"Social": '',
			"FullAddress": "",
			"Address": line_addr,
			"Additional Info": "",
			"Created": "",
			"Comment": "",
			"Updated": ""
		}
		req_params = {"ProductGroupId":"","SortId":1,"Page":1,"PageSize":1000,"SearchText":"","Brand":[],"Weight":[],"Species":[],"BranchId":1,"Terpene":"","Mood":"","THCMAX":100,"THCMIN":0,"CBDMAX":100,"CBDMIN":0,"FromExpressCheckout":False}
		yield scrapy.http.JsonRequest('https://highmountainwebmenu-api.azurewebsites.net/api/products/filterProducts', data=req_params, callback=self.parse_products, headers={"Content-Type": "application/json"})

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
			img_url = 'https://highmountainwebmenu.azurewebsites.net/035c9c51101d29574fbe9c6d9f20eaae.jpg'
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
				"Page URL": f'https://highmountainwebmenu.azurewebsites.net/product/{product["id"]}',
				"Brand": brand,
				"Name": product["name"],
				"SKU": product["sku"],
				"Out stock status": status,
				"Stock count": qt,
				"Currency": "CAD",
				"ccc": "",
				"Price": price,
				"Manufacturer": 'High Mountain',
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
				"p_id": '45830864'
				}
