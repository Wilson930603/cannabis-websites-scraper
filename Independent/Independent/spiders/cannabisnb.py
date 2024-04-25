from Independent.spiders.base_spider import BaseSpider
import scrapy


class CannabisNbSpider(BaseSpider):
	name = 'cannabisnb'
	start_urls = ['https://www.cannabis-nb.com/contact-us/']
	shop_name = 'Cannabis NB'
	p_id = '92761003'
	page = 1
	store_ids = []

	def parse(self, response):
		img = 'https://www.cannabis-nb.com' + response.xpath('//div[@class="cnb-logo logo-desktop"]/a/img/@src').get()
		social = '|'.join(response.xpath('(//section[@class="cnb-social-links"])[1]/a/@href').getall())
		item = {
			"Producer ID": '',
			"p_id": "",
			"Producer": "",
			"Description": "",
			"Link": 'https://www.cannabis-nb.com/',
			"SKU": "",
			"City": "",
			"Province": "",
			"Store Name": self.shop_name,
			"Postal Code": "",
			"long": '',
			"lat": '',
			"ccc": "",
			"Page Url": 'https://www.cannabis-nb.com/',
			"Active": "",
			"Main image": img,
			"Image 2": "",
			"Image 3": "",
			"Image 4": '',
			"Image 5": '',
			"Type": "",
			"License Type": "",
			"Date Licensed": "",
			"Phone": "1 833 821 2195",
			"Phone 2": "",
			"Contact Name": "",
			"EmailPrivate": "",
			"Email": "",
			"Social": social,
			"FullAddress": "",
			"Address": "",
			"Additional Info": "",
			"Created": "",
			"Comment": "",
			"Updated": ""
		}
		yield scrapy.Request('https://www.cannabis-nb.com/stores/', callback=self.parse_locations, meta={'item': item})

	def parse_locations(self, response):
		item = response.meta['item']
		locations = response.xpath('//div[@class="visible-xs"]//p/a[contains(@href, "maps")]/text()').getall()
		cookies = response.xpath('//select[@id="cnb-header-store-pickup"]/option/@value').getall()[1:]
		for location, cookie in zip(locations, cookies):
			shop_id = cookie.split('|')[0]
			self.store_ids.append(shop_id)
			location = location.replace(', Canada', '')
			addr, city, pro_zip = location.rsplit(', ', 2)
			province, postal_code = pro_zip.split(' ', 1)
			item["p_id"] = f"{self.p_id}{shop_id}"
			item["Producer"] = f"{self.shop_name} - {city}"
			item["City"] = city
			item["Province"] = province
			item["Postal Code"] = postal_code
			item["Address"] = addr
			yield item
		headers = {
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:95.0) Gecko/20100101 Firefox/95.0',
			'Accept': '*/*',
			'Accept-Language': 'fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3',
			'Accept-Encoding': 'gzip, deflate, br',
			'Referer': 'https://www.cannabis-nb.com/search/',
			'X-Requested-With': 'XMLHttpRequest',
			'Content-Type': 'application/json; charset=utf-8',
			'Origin': 'https://www.cannabis-nb.com',
			'Connection': 'keep-alive',
			'Sec-Fetch-Dest': 'empty',
			'Sec-Fetch-Mode': 'cors',
			'Sec-Fetch-Site': 'same-origin',
			'TE': 'trailers',
		}
		data = {"FormModel.Sort": "0", "FormModel.Page": str(self.page)}
		yield scrapy.http.JsonRequest('https://www.cannabis-nb.com/search/', headers=headers, data=data, callback=self.parse_menu)

	def parse_menu(self, response):
		products = response.xpath('//a[@class="col-md-3 col-sm-6 col-xs-12 cnb-product"]/@onclick').getall()
		for product in products:
			json_data = eval(product.split("'", 1)[1].rsplit("'", 1)[0].replace('null', 'None').replace('true', 'True').replace('false', 'False'))
			old_price = ''
			if json_data['Pricing']['IsOnPromotion']:
				price = json_data['Pricing']['DiscountedPrice']['Amount']
				old_price = json_data['Pricing']['FullPrice']['Amount']
			else:
				price = json_data['Pricing']['FullPrice']['Amount']
			item = {
				"Page URL": json_data['Url'],
				"Brand": "",
				"Name": json_data['DisplayName'],
				"SKU": "",
				"Out stock status": "",
				"Stock count": "",
				"Currency": "CAD",
				"ccc": "",
				"Price": price,
				"Manufacturer": '',
				"Main image": json_data["Image"],
				"Description": "",
				"Product ID": "",
				"Additional Information": "",
				"Meta description": "",
				"Meta title": "",
				"Old Price": old_price,
				"Equivalency Weights": "",
				"Quantity": '',
				"Weight": "",
				"Option": "",
				"Option type": "",
				"Option Value": "",
				"Option image": "",
				"Option price prefix": "",
				"Cat tree 1 parent": "",
				"Cat tree 1 level 1": '',
				"Cat tree 1 level 2": "",
				"Cat tree 2 parent": "",
				"Cat tree 2 level 1": "",
				"Cat tree 2 level 2": "",
				"Cat tree 2 level 3": "",
				"Image 2": "",
				"Image 3": "",
				"Image 4": "",
				"Image 5": "",
				"Sort order": "",
				"Attribute 1": "CBD",
				"Attribute Value 1": json_data["CBD"],
				"Attribute 2": "THC",
				"Attribute value 2": json_data["THC"],
				"Attribute 3": "",
				"Attribute value 3": '',
				"Attribute 4": "",
				"Attribute value 4": "",
				"Reviews": json_data['RatingCount'],
				"Review link": "",
				"Rating": json_data['TotalRating'],
				"Address": '',
				"p_id": ""
			}
			all_available = {}
			for avail_quantity in json_data['ListStoreAvailableQuantity']:
				all_available[str(avail_quantity['StoreID'])] = avail_quantity['Availability']
			product_in_shops = []
			for shop_id in self.store_ids:
				item_copy = item.copy()
				item_copy['p_id'] = f'{self.p_id}{shop_id}'
				if shop_id in all_available:
					item_copy['Stock count'] = all_available[shop_id]
					if all_available[shop_id] > 0:
						item_copy["Out stock status"] = 'In Stock'
					else:
						item_copy['Stock count'] = 0
						item_copy["Out stock status"] = 'Out of Stock'
				product_in_shops.append(item_copy)
			yield scrapy.Request(json_data['Url'], callback=self.parse_variation, meta={'product_in_shops': product_in_shops})

	def parse_variation(self, response):
		product_in_shops = response.meta['product_in_shops']
		desc = response.xpath('//div[@class="col-xs-12 cnb-desc"]/text()').get().strip().rstrip()
		var_id = response.xpath('//input[@id="code"]/@value').get()
		unique_variation = response.xpath('//span[@class="uniqueVariation"]/text()').get()
		category = response.xpath('//ul[@class="breadcrumb-list"]/li/a/text()').getall()[-1]
		if not unique_variation:
			print(response.url)
		for product_in_shop in product_in_shops:
			product_in_shop['Description'] = desc
			product_in_shop['Product ID'] = var_id
			product_in_shop['Cat tree 1 parent'] = category
			if unique_variation:
				product_in_shop['Weight'] = unique_variation
				yield product_in_shop
