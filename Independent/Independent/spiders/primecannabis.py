from Independent.spiders.base_spider import BaseSpider
import scrapy


class PrimecannabisScraper(BaseSpider):
	name = 'primecannabis'
	start_urls = ["https://primecannabis.ca/shop/"]
	p_ids = ["159837037", "192698735"]
	apis = ['--west-kelowna', 'cranbrook']

	def parse(self, response):
		social = '|'.join(response.xpath('//div[@class="footer-social"]//a/@href').getall()[0:-1])
		locations_html = response.xpath('//div[@class="site-locations-item"]')
		location_links = response.xpath('//div[@class="site-header-b__bottom"]/div[2]/a/@href').getall()
		desc = response.xpath('//div[@class="site-experience"]/p/text()').get()
		for location_html, location_link, p_id, api in zip(locations_html, location_links, self.p_ids, self.apis):
			lines = location_html.xpath('./p[1]//text()').getall()
			addr = lines[0]
			city, province = lines[1].strip().split(', ')
			postal_code = lines[2].strip()
			phone = lines[4]
			email = lines[6]
			yield {
				"Producer ID": '',
				"p_id": p_id,
				"Producer": f"Prime Cannabis - {city}",
				"Description": desc,
				"Link": location_link,
				"SKU": "",
				"City": city,
				"Province": province,
				"Store Name": "Prime Cannabis",
				"Postal Code": postal_code,
				"long": "",
				"lat": "",
				"ccc": "",
				"Page Url": location_link,
				"Active": "",
				"Main image": "https://primecannabis.ca/wp-content/uploads/2020/04/prime-cannabis-logo.svg",
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
			url = f'https://web-dispensary-embed.leafly.com/api/menu/v2/prime-cannabis-{api}'
			meta = {'path': api, 'skip': 0, 'p_id': p_id}
			data = {
				"params": {
					"skip": 0,
					"take": 60
				},
				"cancelToken": {
					"promise": {}
				}
			}
			yield scrapy.http.JsonRequest(url, data=data, callback=self.parse_products, meta=meta)

	def parse_products(self, response):
		products = response.json()["data"]
		p_id = response.meta["p_id"]
		path = response.meta["path"]
		for product in products:
			brand = product['brandName']
			if not brand:
				brand = ''
			stock_count = product.get('stockQuantity')
			if stock_count and stock_count > 0:
				stock_status = 'In Stock'
			else:
				if stock_count is None:
					stock_status = 'Call to confirm'
				else:
					stock_status = 'Out of Stock'
			image = product.get('imageSet')
			image = image.get('high') if image else ''
			reviews = ''
			rating = ''
			catg = ''
			if product.get('strain'):
				reviews = product.get('strain').get('reviewCount')
				rating = product.get('strain').get('averageRating')
				catg = product.get('strain').get('category')
			thc = product["thcContent"]
			cbd = product["cbdContent"]
			if thc:
				if product["thcUnit"] == 'percent':
					thc = f'{thc}%'
				else:
					thc = f'{thc}{product["thcUnit"]}'
			else:
				thc = ''
			if cbd:
				if product["cbdUnit"] == 'percent':
					cbd = f'{cbd}%'
				else:
					cbd = f'{cbd}{product["cbdUnit"]}'
			else:
				cbd = ''
			yield {
				"Page URL": f"https://primecannabis.ca/shop/{path}/",
				"Brand": brand,
				"Name": product.get('name'),
				"SKU": product["id"],
				"Out stock status": stock_status,
				"Stock count": stock_count,
				"Currency": "CAD",
				"ccc": "",
				"Price": product.get('price'),
				"Manufacturer": product.get('dispensaryName'),
				"Main image": product.get('imageUrl'),
				"Description": product.get('description'),
				"Product ID": product["id"],
				"Additional Information": "",
				"Meta description": "",
				"Meta title": "",
				"Old Price": '',
				"Equivalency Weights": "",
				"Quantity": product.get('quantity'),
				"Weight": product.get('displayQuantity'),
				"Option": "",
				"Option type": "",
				"Option Value": "",
				"Option image": "",
				"Option price prefix": "",
				"Cat tree 1 parent": product.get('productCategory'),
				"Cat tree 1 level 1": catg,
				"Cat tree 1 level 2": "",
				"Cat tree 2 parent": "",
				"Cat tree 2 level 1": "",
				"Cat tree 2 level 2": "",
				"Cat tree 2 level 3": "",
				"Image 2": image,
				"Image 3": '',
				"Image 4": '',
				"Image 5": '',
				"Sort order": "",
				"Attribute 1": "CBD",
				"Attribute Value 1": cbd,
				"Attribute 2": "THC",
				"Attribute value 2": thc,
				"Attribute 3": "Product Type",
				"Attribute value 3": product.get('productCategory'),
				"Attribute 4": "",
				"Attribute value 4": "",
				"Reviews": reviews,
				"Review link": "",
				"Rating": rating,
				"Address": '',
				"p_id": p_id
			}
		if products:
			skip = response.meta["skip"] + 60
			url = f'https://web-dispensary-embed.leafly.com/api/menu/v2/prime-cannabis-{path}'
			meta = {'path': path, 'skip': skip, 'p_id': p_id}
			data = {
				"params": {
					"skip": skip,
					"take": 60
				},
				"cancelToken": {
					"promise": {}
				}
			}
			yield scrapy.http.JsonRequest(url, data=data, callback=self.parse_products, meta=meta)
