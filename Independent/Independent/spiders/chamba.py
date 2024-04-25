from Independent.spiders.base_spider import BaseSpider
import scrapy


class ChambaScraper(BaseSpider):
	name = 'chamba'
	start_urls = ['https://www.chamba.ca/']
	shop_name = 'Chamba Cannabis Co.'
	social = ''
	img = ''
	desc = ''

	def parse(self, response):
		self.social = '|'.join(response.xpath('//div[@class="textwidget custom-html-widget"]/a/@href').getall())
		self.img = 'https://923181.smushcdn.com/2283927/wp-content/uploads/2021/02/Chamba_logo_feb16.png?lossy=1&strip=1&webp=1'
		self.desc = '\n'.join(response.xpath('//div[@class="et_pb_row et_pb_row_3"]//p/text()').getall())
		for i in [1, 2]:
			yield scrapy.Request(f'https://chambacannabiswebmenu-api.azurewebsites.net/api/web/home/getStoreRules/{i}', meta={'shop_id': i, 'p_id': f'7643986{i}'}, callback=self.parse_shop, dont_filter=True)

	def parse_shop(self, response):
		shop_id = response.meta['shop_id']
		p_id = response.meta['p_id']
		data = response.json()['data']
		addr_add = data[1]["name"]
		contact_add = data[2]["name"]
		if shop_id == 1:
			link = 'https://www.chamba.ca/landing-shop/'
			addr, city_province, postal_code = addr_add.split(' - ')[1].split(', ')
			city, province = city_province.split(',')
			phone_add, email_add = contact_add.split(' & ')
			phone = phone_add.split(' On ')[1]
			email = email_add.split(' On ')[1]
		else:
			link = 'https://www.chamba.ca/brampton-shop/'
			addr, city_pro_zip = addr_add.split(' at ')[1].rsplit(', ', 1)
			city, province, postal_code = city_pro_zip.split(' ', 2)
			email = ''
			phone = contact_add.split(': ')[1]
		yield {
			"Producer ID": '',
			"p_id": p_id,
			"Producer": f"{self.shop_name} - {city}",
			"Description": self.desc,
			"Link": link,
			"SKU": "",
			"City": city,
			"Province": province,
			"Store Name": self.shop_name,
			"Postal Code": postal_code,
			"long": "",
			"lat": "",
			"ccc": "",
			"Page Url": link,
			"Active": "",
			"Main image": self.img,
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
			"Social": self.social,
			"FullAddress": "",
			"Address": addr,
			"Additional Info": "",
			"Created": "",
			"Comment": "",
			"Updated": ""
		}
		if shop_id == 2:
			req_params = {"ProductGroupId": "", "SortId": 1, "Page": 1, "PageSize": 1000, "SearchText": "", "Brand": [], "Weight": [], "Species": [], "BranchId": 2, "Terpene": "", "Mood": "", "THCMAX": 100, "THCMIN": 0, "CBDMAX": 100, "CBDMIN": 0, "FromExpressCheckout": False}
			yield scrapy.http.JsonRequest('https://chambacannabiswebmenu-api.azurewebsites.net/api/products/filterProducts', data=req_params, callback=self.parse_products, headers={"Content-Type": "application/json"}, dont_filter=True, meta={'p_id': p_id})
		else:
			yield scrapy.Request('https://www.chamba.ca/shop/', meta={'p_id': p_id}, dont_filter=True, callback=self.parse_menu)

	def parse_menu(self, response):
		p_id = response.meta['p_id']
		products = response.xpath('//ul[@class="products columns-3"]/li/a[1]/@href').getall()
		for product_url in products:
			yield scrapy.Request(product_url, meta={'p_id': p_id}, callback=self.parse_product)
		next_page = response.xpath('//a[@class="next page-numbers"]/@href').get()
		if next_page:
			yield scrapy.Request(next_page, meta={'p_id': p_id}, dont_filter=True, callback=self.parse_menu)

	def parse_product(self, response):
		print(response.url)
		p_id = response.meta['p_id']
		name = response.xpath('//h1[@class="product_title entry-title"]/text()').get().strip().rstrip()
		price = response.xpath('//p[@class="price"]/span/bdi/text()').get()
		img_url = response.xpath('//div[@class="woocommerce-product-gallery__image"]/a/@href').get()
		sku = response.xpath('//span[@class="sku"]/text()').get()
		cat = response.xpath('//span[@class="posted_in"]/a/text()').get()
		product_id = response.xpath('//button[@name="add-to-cart"]/@value').get()
		stock = response.xpath('//p[@class="stock in-stock"]/text()').get()
		weight = response.xpath('//tr[@class="woocommerce-product-attributes-item woocommerce-product-attributes-item--weight"]/td/text()').get()
		in_desc = response.xpath('//div[@class="woocommerce-product-details__short-description"]/p/text()').getall()
		thc_name = ''
		thc = ''
		cbd_name = ''
		cbd = ''
		brand = ''
		for desc in in_desc:
			if 'Brand' in desc:
				brand = desc.split(':')[1].strip().rstrip()
			elif 'THC' in desc:
				thc = desc.split(':')[1].strip().rstrip()
				thc_name = 'THC'
			elif 'CBD' in desc:
				cbd = desc.split(':')[1].strip().rstrip()
				cbd_name = 'THC'
		if stock:
			status = 'In Stock'
			qt = int(stock.strip().split(' in')[0])
		else:
			status = 'Out of Stock'
			qt = 0
		description = response.xpath('//div[@id="tab-description"]/p/text()').get()
		yield {
			"Page URL": response.url,
			"Brand": brand,
			"Name": name,
			"SKU": sku,
			"Out stock status": status,
			"Stock count": qt,
			"Currency": "CAD",
			"ccc": "",
			"Price": price,
			"Manufacturer": self.shop_name,
			"Main image": img_url,
			"Description": description,
			"Product ID": product_id,
			"Additional Information": '',
			"Meta description": "",
			"Meta title": "",
			"Old Price": '',
			"Equivalency Weights": '',
			"Quantity": "",
			"Weight": weight,
			"Option": "",
			"Option type": '',
			"Option Value": "",
			"Option image": "",
			"Option price prefix": "",
			"Cat tree 1 parent": cat,
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

	def parse_products(self, response):
		p_id = response.meta['p_id']
		products = response.json()["data"]["products"]
		brands = self.settings.get('BRANDS', [])
		brands_lower = [x.lower() for x in brands]
		for product in products:
			brand = product['brand']
			if not brand:
				brand = product['name'].split(' - ')[0]
			if brand and brands and brand.lower() not in brands_lower:
				self.logger.debug(f'Ignore brand: {brand}')
				continue
			qt = int(product["quantity"])
			status = "In Stock"
			if qt == 0:
				status = "Out of Stock"
			img_url = 'https://chambacannabiswebmenu.azurewebsites.net/035c9c51101d29574fbe9c6d9f20eaae.jpg'
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
			old_price = ''
			if price == discounted_price:
				discounted_price = ''
			if discounted_price:
				old_price = price
				price = discounted_price
			yield {
				"Page URL": f"https://chambacannabiswebmenu.azurewebsites.net/product/{product['id']}",
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
