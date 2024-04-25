from Independent.spiders.base_spider import BaseSpider
import scrapy


class ThecannabisguysScraper(BaseSpider):
	name = 'thecannabisguys'
	shop_name = 'The Cannabis Guys'
	p_id = 687528701

	def start_requests(self):
		yield scrapy.Request('https://www.thecannabisguys.ca/', callback=self.parse)


	def parse(self, response):
		social = response.xpath('//div[@id="comp-kn4zo0rh"]/h2/a/@href').get()
		email = response.xpath('//div[@id="comp-kng8gaw3"]//text()').get()
		img = response.xpath('//img[@alt="Emblem-Knockout-RGB.png"]/@src').get()

		contact = response.xpath('//div[@id="comp-kue4pako4"]/h3/span/span/span//text()').getall()
		addr = contact[0].rstrip()
		city, pro_zip = contact[2].split(', ')
		province, postal_code = pro_zip.split(' ', 1)
		phone = contact[5].replace('-', ' ')
		data = []
		data.append([city, province, postal_code, phone, addr])

		ind = 0
		shop_links = [
			'https://shop.thecannabisguys.ca/embed/stores/3389/menu',
		]
		for obj in data:
			p_id = self.p_id + ind
			link = shop_links[ind]
			yield {
				"Producer ID": '',
				"p_id": p_id,
				"Producer": f"{self.shop_name} - {obj[0]}",
				"Description": '',
				"Link": link,
				"SKU": "",
				"City": obj[0],
				"Province": obj[1],
				"Store Name": self.shop_name,
				"Postal Code": obj[2],
				"long": '',
				"lat": '',
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
				"Phone": obj[3],
				"Phone 2": "",
				"Contact Name": "",
				"EmailPrivate": "",
				"Email": email,
				"Social": social,
				"FullAddress": "",
				"Address": obj[4],
				"Additional Info": "",
				"Created": "",
				"Comment": "",
				"Updated": ""
			}
			if ind == 0:
				data = {
					"requests": [
						{
							"indexName": "menu-products-production",
							"params": "highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&hitsPerPage=1000&filters=store_id=3389&userToken=DqpSiBSCQSDgdlL986J5P&enablePersonalization=true&personalizationImpact=75&page=0&facets=%5B%5D&tagFilters="
						}
					]
				}
				yield scrapy.http.JsonRequest('https://vfm4x0n23a-dsn.algolia.net/1/indexes/*/queries?x-algolia-agent=Algolia%20for%20JavaScript%20(4.5.1)%3B%20Browser%20(lite)%3B%20JS%20Helper%20(3.1.1)%3B%20react%20(16.13.1)%3B%20react-instantsearch%20(6.4.0)&x-algolia-api-key=b499e29eb7542dc373ec0254e007205d&x-algolia-application-id=VFM4X0N23A', data=data, callback=self.parse_products)
			break

	def parse_products(self, response):
		products = response.json()["results"][0]["hits"]
		brands = self.settings.get('BRANDS', [])
		brands_lower = [x.lower() for x in brands]
		for product in products:
			brand = product["brand"]
			if not brand:
				brand = product['name'].split(' - ')[0]
			if brand and brands and brand.lower() not in brands_lower:
				self.logger.debug(f'Ignore brand: {brand}')
				continue
			link = f'https://shop.thecannabisguys.ca/embed/stores/3389/products/{product["product_id"]}/{product["url_slug"]}'
			print(link)
			stock = 'Out of Stock'
			if product["max_cart_quantity"] > 0:
				stock = 'In Stock'
			img = ''
			if product["has_photos"]:
				img = product["image_urls"][0]
			cbd_name = ''
			cbd = ''
			if product["percent_cbd"] > 0:
				cbd_name = 'CBD'
				cbd = f'{product["percent_cbd"]}%'
			elif product["dosage"]:
				cbd_name = 'CBD'
				cbd = product["dosage"].split(' ')[0]
			thc_name = ''
			thc = ''
			if product["percent_thc"] > 0:
				thc_name = 'THC'
				thc = f'{product["percent_thc"]}%'
			rating = ''
			try:
				if product['review_count'] > 0:
					rating = product['aggregate_rating']
				weight = product['available_weights'][0]
				price = product[f'price_{weight}'.replace(' ', '_')]
			except:
				weight = ''
				price = product[f'price_each']
			desc = product['store_notes']
			if desc:
				desc = desc.replace('’', "'")
			else:
				desc = ''
			yield {
				"Page URL": link,
				"Brand": brand,
				"Name": product["name"],
				"SKU": '',
				"Out stock status": stock,
				"Stock count": '',
				"Currency": "CAD",
				"ccc": "",
				"Price": price,
				"Manufacturer": self.shop_name,
				"Main image": img,
				"Description": desc,
				"Product ID": product['product_id'],
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
				"Cat tree 1 parent": product["type"],
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
				"Reviews": product['review_count'],
				"Review link": "",
				"Rating": rating,
				"Address": '',
				"p_id": self.p_id
			}
