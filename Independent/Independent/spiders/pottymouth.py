from Independent.spiders.base_spider import BaseSpider
import scrapy


class PottyMouthSpider(BaseSpider):
	name = 'pottymouth'
	shop_name = 'Potty Mouth Cannabis Co.'
	p_id = 8621109
	start_urls = ['http://pottymouthcannabis.com/about']
	all_weights = {
		'gram': '1g',
		'two gram': '2g',
		'eighth ounce': '3.5g',
		'quarter ounce': '7g',
		'half ounce': '14g',
		'ounce': '28g'
	}

	def parse(self, response):
		img = response.xpath('//a[@class="raven-site-logo-link"]/img/@src').get()
		desc = '\n'.join(response.xpath('//div[@data-id="eb55033"]/div/p//text()').getall())
		email = response.xpath('//div[@data-id="8d8746b"]/div/div/div[2]//a/text()').get().strip().rstrip()
		phone = response.xpath('//div[@data-id="cf3e2cd"]/div/h2/a/span[2]/span/text()').get().replace('-', '').strip().rstrip()
		contacts = response.xpath('//div[@data-id="1861e77"]//h3/span/text()').getall()
		contacts = [contact.strip().rstrip() for contact in contacts]
		addr = contacts[1]
		city, pro_zip = contacts[2].split(', ')
		province, postal_code = pro_zip.split(' ', 1)
		social = response.xpath('//div[@data-id="e55fa69"]//a/@href').get()
		yield {
			"Producer ID": '',
			"p_id": self.p_id,
			"Producer": f"{self.shop_name} - {city}",
			"Description": desc,
			"Link": 'http://pottymouthcannabis.com/',
			"SKU": "",
			"City": city,
			"Province": province,
			"Store Name": self.shop_name,
			"Postal Code": '',
			"long": '',
			"lat": '',
			"ccc": "",
			"Page Url": 'http://pottymouthcannabis.com/',
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
		data = {
			"requests": [
				{
					"indexName": "menu-products-production",
					"params": "highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&hitsPerPage=1000&filters=store_id%20%3D%203476&userToken=3u6HaHaST4RNYamz4zRzA&enablePersonalization=true&personalizationImpact=75&page=0&facets=%5B%5D&tagFilters="
				}
			]
		}
		yield scrapy.http.JsonRequest('https://vfm4x0n23a-dsn.algolia.net/1/indexes/*/queries?x-algolia-agent=Algolia%20for%20JavaScript%20(4.5.1)%3B%20Browser%20(lite)%3B%20JS%20Helper%20(3.1.1)%3B%20react%20(16.13.1)%3B%20react-instantsearch%20(6.4.0)&x-algolia-api-key=b499e29eb7542dc373ec0254e007205d&x-algolia-application-id=VFM4X0N23A', data=data, callback=self.parse_products)

	def parse_products(self, response):
		products = response.json()["results"][0]["hits"]
		for product in products:
			stock = 'Out of Stock'
			if product["max_cart_quantity"] > 0:
				stock = 'In Stock'
			img = product['image_urls'][0] if product['image_urls'] else ''
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
				weight = self.all_weights[weight]
			except:
				weight = ''
				price = product[f'price_each']
			desc = product["description"]
			yield {
				"Page URL": 'http://pottymouthcannabis.com/order-online',
				"Brand": product["brand"],
				"Name": product["name"],
				"SKU": '',
				"Out stock status": stock,
				"Stock count": '',
				"Currency": "CAD",
				"ccc": "",
				"Price": price,
				"Manufacturer": '',
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
				"Reviews": product['review_count'] if product['review_count'] > 0 else '',
				"Review link": "",
				"Rating": rating,
				"Address": '',
				"p_id": self.p_id
			}
