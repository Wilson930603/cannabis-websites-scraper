from Independent.spiders.base_spider import BaseSpider
import scrapy


class StickyleafScraper(BaseSpider):
	name = 'stickyleaf'
	branches = [{'id': 2, 'city': "Okanagan Falls", 'p_id': '58724376'}, {'id': 1, 'city': "Creston", 'p_id': '838764873'}]
	start_urls = ["https://stickyleaf.ca/contact-us/"]

	def parse(self, response):
		img = response.xpath('//div[@class="logo_container"]/a/img/@src').get()
		html_extract = response.xpath('//div[@class="et_pb_text_inner"]/p')
		contact = html_extract[0].get().replace('%20', ' ').replace('&gt;', '>').replace('&lt;', '<')
		phone, email = contact.split('</a>', 1)
		phone = phone.split('>')[2]
		email = email.split('mailto')[1].split('>')[1].split('<')[0]
		locations = [html_extract[1], html_extract[2]]
		for location_html, branch_data in zip(locations, self.branches):
			rows = location_html.xpath('./text()').getall()
			address = rows[0]
			if address[-1] == ',':
				address = address[0:-1]
			province, postal_code = rows[1].strip().split(', ')
			city = branch_data['city']
			p_id = branch_data['p_id']
			yield {
				"Producer ID": '',
				"p_id": p_id,
				"Producer": f"Sticky Leaf - {city}",
				"Description": '',
				"Link": "https://stickyleaf.ca/",
				"SKU": "",
				"City": city,
				"Province": province,
				"Store Name": "Sticky Leaf",
				"Postal Code": "",
				"long": "",
				"lat": "",
				"ccc": "",
				"Page Url": "https://stickyleaf.ca/",
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
				"Address": address,
				"Additional Info": "",
				"Created": "",
				"Comment": "",
				"Updated": ""
			}
			req_params = {"ProductGroupId": "", "SortId": 1, "Page": 1, "PageSize": 1000, "SearchText": "", "Brand": [], "Weight": [], "Species": [], "BranchId": branch_data['id'], "Terpene": "", "Mood": "", "THCMAX": 100, "THCMIN": 0, "CBDMAX": 100, "CBDMIN": 0, "FromExpressCheckout": False}
			yield scrapy.http.JsonRequest('https://stickyleafwebmenu-api.azurewebsites.net/api/products/filterProducts', data=req_params, callback=self.parse_products, headers={"Content-Type": "application/json"}, dont_filter=True, meta={"p_id": p_id})

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
			img_url = 'https://stickyleafwebmenu.azurewebsites.net/035c9c51101d29574fbe9c6d9f20eaae.jpg'
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
				"Page URL": f'https://stickyleafwebmenu.azurewebsites.net/product/{product["id"]}',
				"Brand": brand,
				"Name": product["name"],
				"SKU": product["sku"],
				"Out stock status": status,
				"Stock count": qt,
				"Currency": "CAD",
				"ccc": "",
				"Price": price,
				"Manufacturer": 'Sticky Leaf',
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
