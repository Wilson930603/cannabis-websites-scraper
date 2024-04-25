from Independent.spiders.base_spider import BaseSpider
import scrapy


class ShelterMarketSpider(BaseSpider):
	name = 'sheltermarket'
	shop_name = 'Shelter Market'
	p_id = '618972201'
	start_urls = ['https://sheltermarket.ca/contact-us']

	def parse(self, response):
		email = response.xpath('//div[@class="blockRenderer_container__2cZhF body-2 body-2--tall"]/p[5]/strong/a/text()').get()
		phone = response.xpath('//div[@class="blockRenderer_container__2cZhF body-2 body-2--tall"]/p[6]/strong/text()').get().strip().replace('+', '')
		address = response.xpath('//div[@class="footer_credits__2mWjm"]/span[2]/text()').get()
		addr, city, province, postal_code = address.split(', ')
		social = '|'.join(response.xpath('//div[@class="footer_social__16bpp"]/a/@href').getall())
		yield {
			"Producer ID": '',
			"p_id": self.p_id,
			"Producer": f"{self.shop_name} - {city}",
			"Description": '',
			"Link": 'https://sheltermarket.ca/',
			"SKU": "",
			"City": city,
			"Province": province,
			"Store Name": self.shop_name,
			"Postal Code": '',
			"long": '',
			"lat": '',
			"ccc": "",
			"Page Url": 'https://sheltermarket.ca/',
			"Active": "",
			"Main image": '',
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
					"indexName": "prod_Products",
					"params": "highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&filters=published%3Atrue%20AND%20shopify.inventory%3Atrue%20AND%20scope%3ARecreational%20AND%20availability%3ASK&analytics=true&maxValuesPerFacet=20&page=0&hitsPerPage=1000&facets=%5B%5D&tagFilters="
				}
			]
		}
		yield scrapy.http.JsonRequest('https://3bkeo29ov5-dsn.algolia.net/1/indexes/*/queries?x-algolia-agent=Algolia%20for%20JavaScript%20(4.10.5)%3B%20Browser%20(lite)%3B%20JS%20Helper%20(3.5.5)%3B%20react%20(17.0.2)%3B%20react-instantsearch%20(6.12.1)&x-algolia-api-key=4efb19cec2ac0b71a95739d729e67140&x-algolia-application-id=3BKEO29OV5', data=data, callback=self.parse_menu)

	def parse_menu(self, response):
		products = response.json()["results"][0]["hits"]
		for product in products:
			cbd_name = ''
			cbd = ''
			thc_name = ''
			thc = ''
			try:
				if product['cbd'] != 0:
					cbd_name = 'CBD'
					cbd = f'{product["cbd"]}{product["niceUnit"]}'
			except:
				try:
					if product['cbdPercent'] != 0:
						cbd_name = 'CBD'
						cbd = f'{product["cbdPercent"]}%'
				except:
					pass
			try:
				if product['thc'] != 0:
					thc_name = 'THC'
					thc = f'{product["thc"]}%'
			except:
				try:
					if product['thcPercent'] != 0:
						thc_name = 'THC'
						thc = f'{product["thcPercent"]}%'
				except:
					pass
			eq_weight = ''
			try:
				eq_weight = f'{product["driedCannabis"]}g'
			except:
				pass
			item = {
				"Page URL": f'https://sheltermarket.ca/products/{product["shopify"]["handle"]}',
				"Brand": product["brand"]["name"],
				"Name": product["title"],
				"SKU": product["shopify"]["sku"],
				"Out stock status": "In Stock",
				"Stock count": '',
				"Currency": "CAD",
				"ccc": "",
				"Price": "",
				"Manufacturer": '',
				"Main image": product["image"],
				"Description": "",
				"Product ID": "",
				"Additional Information": '',
				"Meta description": "",
				"Meta title": "",
				"Old Price": '',
				"Equivalency Weights": eq_weight,
				"Quantity": "",
				"Weight": "",
				"Option": "",
				"Option type": '',
				"Option Value": "",
				"Option image": "",
				"Option price prefix": "",
				"Cat tree 1 parent": product["shopify"]["product_type"],
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
				"Reviews": "",
				"Review link": "",
				"Rating": "",
				"Address": '',
				"p_id": self.p_id
			}
			yield scrapy.Request(f'https://sheltermarket.ca/_next/data/zUxEtJcxxPH_oEBmhHckI/products/{product["shopify"]["handle"]}.json', callback=self.parse_product, meta={'item': item})

	def parse_product(self, response):
		item = response.meta['item']
		product = response.json()['pageProps']['data']['product']
		nb_variants = len(product["options"][0]["values"].split(', '))
		print(item["Page URL"])
		if nb_variants > 1:
			item["Option type"] = "Choose a size"
		for variant in product["variants"]:
			if variant['scope'] == 'Recreational' and variant["lot"]:
				item["Weight"] = variant["size"]
				item["Price"] = variant["price"]
				item["Product ID"] = variant["_id"]
				item["Description"] = variant["lot"]["description"]
				if nb_variants > 1:
					item["Option Value"] = variant['size']
					item["Option price prefix"] = variant["price"]
				yield item
