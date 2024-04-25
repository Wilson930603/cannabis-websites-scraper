import json

from Independent.spiders.base_spider import BaseSpider
import scrapy


class MyNslcSpider(BaseSpider):
	name = 'mynslc'
	start_urls = ['https://cannabis.mynslc.com/ac/storelocations']
	p_id_base = '66152'
	shop_name = 'MyNSLC Cannabis'

	def parse(self, response):
		stores = response.json()
		for store in stores:
			needed = False
			for feature in store['features']:
				if feature['featureId'] == 'CP':
					needed = True
					break
			if needed:
				yield {
					"Producer ID": '',
					"p_id": f'{self.p_id_base}{store["id"]}',
					"Producer": f'{self.shop_name}',
					"Description": "",
					"Link": f"https://cannabis.mynslc.com/en/Stores/Store_{store['id']}",
					"SKU": "",
					"City": store["addressInfo"]["city"],
					"Province": store["addressInfo"]["province"],
					"Store Name": store["name"],
					"Postal Code": store["addressInfo"]["postal"],
					"long": store["coordinates"]["lng"],
					"lat": store["coordinates"]["lat"],
					"ccc": "",
					"Page Url": f"https://cannabis.mynslc.com/en/Stores/Store_{store['id']}",
					"Active": "",
					"Main image": "https://cannabis.mynslc.com/skins/cannabis/images/logo.png",
					"Image 2": '',
					"Image 3": '',
					"Image 4": '',
					"Image 5": '',
					"Type": "",
					"License Type": "",
					"Date Licensed": "",
					"Phone": store["phone"].replace('-', ' '),
					"Phone 2": "",
					"Contact Name": "",
					"EmailPrivate": "",
					"Email": "",
					"Social": "",
					"FullAddress": "",
					"Address": store["addressInfo"]["address1"],
					"Additional Info": "",
					"Created": "",
					"Comment": "",
					"Updated": ""
				}
				data = '{"options":{"Start":0,"Length":1000,"IncludeFacets":true,"Keywords":null,"ProductType":"","ArticleIds":null,"Facets":{"ProductCategoryKey":{"IsShown":true,"Values":null},"Terpenes":{"IsShown":true,"Values":null},"StrainProfile":{"IsShown":true,"Values":null},"CannabisType":{"IsShown":true,"Values":null},"BrandName":{"IsShown":true,"Values":null},"CbdLevel":{"IsShown":true,"Values":null},"ThcLevel":{"IsShown":true,"Values":null},"Flavours":{"IsShown":true,"Values":null},"IsLocal":{"IsShown":true,"Values":null},"Store":{"IsShown":true,"Values":["'+str(store["id"])+'"]},"IsAvailableOnline":{"IsShown":true,"Values":null}},"SortOrder":"Name","PadResultsWhenSupplyingArticleIds":true,"WebsiteCategory":"Cannabis","WebsiteSubcategory":""}}'
				headers = {
					'authority': 'cannabis.mynslc.com',
					'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36',
					'content-type': 'application/json; charset=UTF-8',
					'accept': 'application/json, text/javascript, */*; q=0.01',
					'origin': 'https://cannabis.mynslc.com',
					'cookie': f'age-verification-redirect=/products/cannabis; store_id={store["id"]};'
				}
				yield scrapy.Request('https://cannabis.mynslc.com/Services/Cannabis/ProductSearchService.svc/GetResultSet', method='POST', body=data, callback=self.parse_menu, headers=headers, dont_filter=True, meta={'id': store['id'], 'name': store['name']})

	def parse_menu(self, response):
		store_id = response.meta['id']
		store_name = response.meta['name']
		products = response.json()['d']['Hits']
		headers = {
			'authority': 'cannabis.mynslc.com',
			'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36',
			'content-type': 'application/json; charset=UTF-8',
			'accept': 'application/json, text/javascript, */*; q=0.01',
			'origin': 'https://cannabis.mynslc.com',
			'cookie': f'store_id={store_id}; cannabis#lang=en; ASP.NET_SessionId=d2mb3enxt2tytpc1to5u2etl; SC_ANALYTICS_GLOBAL_COOKIE=b6dcfdfc7ff7454d8f9de324eefb352f|False; akaalb_cannabis_label=~op=cannabis_mynslc_com:origin3_cannabis|~rv=47~m=origin3_cannabis:0|~os=adedd81c3128b52156e33235fdb436bf~id=53f5a8f667e6941bb6d1f609395519dd; _ga=GA1.3.505509715.1639248962; _gid=GA1.3.1141309538.1639248962; _gat_%5Bobject%20Object%5D=1; _gat_UA-9669691-14=1; __RequestVerificationToken=4MUfKxPwjr46A95NL7v6Vd9gvDnHTuuUc2iJvjWByuQLfE9IFMjV3ixfRn1ys_1ZoFHDBpuXOgXjQUSQIGbEYyoHeCs1; ai_user=Ca6n9CDUGoPSoZ5CJ7q48V|2021-12-11T18:56:36.846Z; ac_customerId=jYbDXa1i3g06AbwCcR2T58hvajz5x2zsKmf5AmFnLMgEDkmoZgMa4oT6prolTDk07S05e-iDSrL5M0usBLt_whLZGEsTaIyacKgRjEGcH5rqJeP30; _ga=GA1.2.505509715.1639248962; _gid=GA1.2.1141309538.1639248962; ai_session=IVu9FYgO+xZ86608DQ7Pki|1639248999270|1639248999270; LaVisitorNew=Y; LaVisitorId_dDRnLmxhZGVzay5jb20v=9ma6ha9iupec50vembj6dbm5pd9j9; LaSID=dz0k16b4rcxd0iplszitgjz664d59; _gat_UA-9669691-12=1; _gat_UA-9669691-13=1'
		}
		for product in products:
			item = {
				"Page URL": f'https://cannabis.mynslc.com{product["ItemUrl"]}',
				"Brand": product["BrandDisplayName"],
				"Name": product["DisplayName"],
				"SKU": "",
				"Out stock status": 'In Stock' if product['IsAvailableOnline'] else 'Out of Stock',
				"Stock count": '',
				"Currency": "CAD",
				"ccc": "",
				"Price": product['ProductStartingPrice'],
				"Manufacturer": store_name,
				"Main image": f'https://cannabis.mynslc.com{product["ImageUrl"]}',
				"Description": product['ProductSearchContent'],
				"Product ID": product["ProductCode"],
				"Additional Information": '',
				"Meta description": "",
				"Meta title": "",
				"Old Price": "",
				"Equivalency Weights": '',
				"Quantity": "",
				"Weight": "",
				"Option": "",
				"Option type": '',
				"Option Value": "",
				"Option image": "",
				"Option price prefix": "",
				"Cat tree 1 parent": product["WebsiteCategory"],
				"Cat tree 1 level 1": product["WebsiteSubcategory"],
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
				"Attribute 1": "CBD",
				"Attribute Value 1": product["CBDDisplayValue"],
				"Attribute 2": "THC",
				"Attribute value 2": product["THCDisplayValue"],
				"Attribute 3": "",
				"Attribute value 3": '',
				"Attribute 4": "",
				"Attribute value 4": "",
				"Reviews": '',
				"Review link": "",
				"Rating": '',
				"Address": '',
				"p_id": f'{self.p_id_base}{store_id}'
			}
			yield item
			# yield scrapy.Request(f'https://cannabis.mynslc.com{product["ItemUrl"]}', callback=self.parse_product, meta={'item': item}, headers=headers)

	def parse_product(self, response):
		print(response.url)
		item = response.meta['item']
		weight, price = response.xpath('//span[@class="Product_Info-variant_amount"]/text()').get().split(' - $')
		other_images = response.xpath('//div[@class="Product_Gallery-thumbnail slick-slide slick-active"]/img/@src').getall()
		item['Image 2'] = 'https://cannabis.mynslc.com' + other_images[0] if len(other_images) > 0 else ''
		item['Image 3'] = 'https://cannabis.mynslc.com' + other_images[1] if len(other_images) > 1 else ''
		item['Image 4'] = 'https://cannabis.mynslc.com' + other_images[2] if len(other_images) > 2 else ''
		item['Image 5'] = 'https://cannabis.mynslc.com' + other_images[3] if len(other_images) > 3 else ''
		item['Price'] = price
		item['Weight'] = weight
		yield item
