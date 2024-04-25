from Independent.spiders.base_spider import BaseSpider
import scrapy


class KitscannabisScraper(BaseSpider):
	name = 'kitscannabis'
	start_urls = ['https://www.kitscannabis.ca/']
	p_id = '16346203'

	def parse(self, response):
		img = response.xpath('//a[@data-animation-role="header-element"]/img/@src').get()
		contact = response.xpath('//div[@id="block-yui_3_17_2_1_1623349024206_56687"]/div/h4/text()').getall()
		phone = contact[0].split(' ')[1]
		address, city = contact[1].split(': ')[1].split(', ')
		desc = response.xpath('//div[@class="image-card sqs-dynamic-text-container"]/div[2]//text()').get()
		yield {
			'Producer ID': '',
			'p_id': self.p_id,
			'Producer': f"Khatsahlano Kannabis - {city}",
			'Description': desc,
			'Link': 'https://www.kitscannabis.ca/',
			'SKU': '',
			'City': city,
			'Province': 'BC',
			'Store Name': "Khatsahlano Kannabis",
			'Postal Code': 'V6K 3E4',
			'long': '',
			'lat': '',
			'ccc': '',
			'Page Url': 'https://www.kitscannabis.ca/',
			'Active': '',
			'Main image': img,
			'Image 2': '',
			'Image 3': '',
			'Image 4': '',
			'Image 5': '',
			'Type': '',
			'License Type': '',
			'Date Licensed': '',
			'Phone': phone,
			'Phone 2': '',
			'Contact Name': '',
			'EmailPrivate': '',
			'Email': '',
			'Social': '',
			'FullAddress': address,
			'Address': '',
			'Additional Info': '',
			'Created': '',
			'Comment': '',
			'Updated': ''
		}
		data = {
			"requests": [
				{
					"indexName": "menu-products-production",
					"params": "highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&hitsPerPage=1000&filters=store_id%20%3D%203376&userToken=kh7e9c61yDVStdelPWd45&enablePersonalization=true&personalizationImpact=75&page=0&facets=%5B%5D&tagFilters="
				}
			]
		}
		yield scrapy.http.JsonRequest('https://vfm4x0n23a-3.algolianet.com/1/indexes/*/queries?x-algolia-agent=Algolia%20for%20JavaScript%20(4.5.1)%3B%20Browser%20(lite)%3B%20JS%20Helper%20(3.1.1)%3B%20react%20(16.13.1)%3B%20react-instantsearch%20(6.4.0)&x-algolia-api-key=b499e29eb7542dc373ec0254e007205d&x-algolia-application-id=VFM4X0N23A', data=data, callback=self.parse_products)

	def parse_products(self, response):
		products = response.json()["results"][0]["hits"]
		for product in products:
			stock = 'Out of Stock'
			if product["max_cart_quantity"] > 0:
				stock = 'In Stock'
			img = ''
			if product["has_photos"]:
				img = product["image_urls"][0]
			dsc = product["description"]
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
			if product['review_count'] > 0:
				rating = product['aggregate_rating']
			yield {
				"Page URL": 'https://www.kitscannabis.ca/shop/',
				"Brand": product["brand"],
				"Name": product["name"],
				"SKU": '',
				"Out stock status": stock,
				"Stock count": '',
				"Currency": "CAD",
				"ccc": "",
				"Price": product["sort_price"],
				"Manufacturer": '',
				"Main image": img,
				"Description": product["store_notes"],
				"Product ID": product['product_id'],
				"Additional Information": '',
				"Meta description": "",
				"Meta title": "",
				"Old Price": '',
				"Equivalency Weights": '',
				"Quantity": "",
				"Weight": '',
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
