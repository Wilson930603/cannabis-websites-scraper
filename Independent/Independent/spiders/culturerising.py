import re

from Independent.spiders.base_spider import BaseSpider
import scrapy


class CultureRisingSpider(BaseSpider):
	name = 'culturerising'
	shop_name = 'Culture Rising Cannabis'
	p_id = 176398210
	start_urls = ['https://cannabis.culturerising.ca/']

	def parse(self, response):
		img = response.xpath('//img[@itemprop="logo"]/@src').get()
		phone = response.xpath('//a[@aria-label="Call"]/text()').get().replace('-', ' ')
		address = response.xpath('//p[@class="footer-nav__text footer-nav__text--address"]/text()').getall()
		addr = address[0].strip()
		city, province = address[1].strip().split(' ')
		postal_code = address[2].strip().rstrip().rsplit(' ', 1)[0]
		yield {
			"Producer ID": '',
			"p_id": self.p_id,
			"Producer": f'{self.shop_name} - {city}',
			"Description": "",
			"Link": "https://cannabis.culturerising.ca/",
			"SKU": "",
			"City": city,
			"Province": province,
			"Store Name": self.shop_name,
			"Postal Code": postal_code,
			"long": "",
			"lat": "",
			"ccc": "",
			"Page Url": "https://cannabis.culturerising.ca/",
			"Active": "",
			"Main image": f'https:{img}',
			"Image 2": '',
			"Image 3": '',
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
			"Social": "",
			"FullAddress": "",
			"Address": addr,
			"Additional Info": "",
			"Created": "",
			"Comment": "",
			"Updated": ""
		}
		yield scrapy.Request('https://cannabis.culturerising.ca/collections/all', callback=self.parse_menu)

	def parse_menu(self, response):
		products = response.xpath('//div[@class="product-top"]/a[@class="product-link js-product-link"]/@href').getall()
		for product in products:
			yield scrapy.Request(f'https://cannabis.culturerising.ca{product}.js', callback=self.parse_product)
		next_link = response.xpath('//span[@class="next"]/a/@href').get()
		if next_link:
			next_link = f'https://cannabis.culturerising.ca{next_link}'
			yield scrapy.Request(next_link, callback=self.parse_menu)

	def parse_product(self, response):
		product = response.json()
		thc = ''
		thc_name = ''
		cbd = ''
		cbd_name = ''
		weight = ''
		for tag in product['tags']:
			if tag.startswith('CBD Content (Max):'):
				cbd_name = 'CBD'
				cbd = tag.split(':')[1]
			elif tag.startswith('THC Content (Max):'):
				thc_name = 'THC'
				thc = tag.split(':')[1]
			elif tag.startswith('Net Weight:'):
				weight = f"{tag.split(':')[1]}g"
		cleanr = re.compile('<.*?>')
		desc = product['description'] if product['description'] else ''
		desc = re.sub(cleanr, '', desc)
		item = {
			"Page URL": f"https://cannabis.culturerising.ca/products/{product['handle']}",
			"Brand": product['vendor'].replace('-', ''),
			"Name": product['title'],
			"SKU": '',
			"Out stock status": '',
			"Stock count": "",
			"Currency": "CAD",
			"ccc": "",
			"Price": '',
			"Manufacturer": self.shop_name,
			"Main image": product['media'][0]['src'],
			"Description": desc,
			"Product ID": product['id'],
			"Additional Information": "",
			"Meta description": "",
			"Meta title": "",
			"Old Price": '',
			"Equivalency Weights": "",
			"Quantity": '',
			"Weight": weight,
			"Option": "",
			"Option type": "",
			"Option Value": "",
			"Option image": "",
			"Option price prefix": "",
			"Cat tree 1 parent": product['type'].replace(' Product', ''),
			"Cat tree 1 level 1": '',
			"Cat tree 1 level 2": "",
			"Cat tree 2 parent": "",
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
			"p_id": self.p_id
		}
		nb_variants = len(product['variants'])
		for variant in product['variants']:
			item['SKU'] = variant['sku']
			in_stock = 'Out of Stock'
			if variant['available']:
				in_stock = 'In Stock'
			item['Out stock status'] = in_stock
			price = variant['price'] / 100
			item['Price'] = price
			if nb_variants > 1:
				item["Option type"] = "Choose a size"
				item["Option Value"] = variant['title']
				item["Option price prefix"] = price
			yield item
