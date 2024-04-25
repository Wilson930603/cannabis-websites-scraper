import json

from Independent.spiders.base_spider import BaseSpider
import scrapy
import re


class PineapplevictoriaSpider(BaseSpider):
	name = 'pineapplevictoria'
	start_urls = ['https://shop.pineapplevictoria.ca/contact-us/']
	p_id = '8634588'

	def parse(self, response):
		html_content = response.xpath('//div[@class="col-md-12 textcategory"]/p')
		phone = html_content[0].xpath('./a/text()').get()
		email = html_content[1].xpath('./text()[2]').get()
		address = html_content[2].xpath('./text()').get().replace('&nbsp;', '').rstrip().split(' ', 1)[1]
		city, province = html_content[3].xpath('./text()').get().split(': ')[1].split(', ')
		img = response.xpath('//div[@class="vertical logo"]/a/img/@src').get()
		shop = {
			"Producer ID": '',
			"p_id": self.p_id,
			"Producer": f"Pineapple Express - {city}",
			"Description": '',
			"Link": "https://pineapplevictoria.ca/",
			"SKU": "",
			"City": city,
			"Province": province,
			"Store Name": "Pineapple Express",
			"Postal Code": "V9A3L4",
			"long": "",
			"lat": "",
			"ccc": "",
			"Page Url": "https://pineapplevictoria.ca/",
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
		yield scrapy.Request('https://shop.pineapplevictoria.ca/service/about/', meta={'shop': shop}, callback=self.parse_additional)

	def parse_additional(self, response):
		shop = response.meta['shop']
		desc = response.xpath('//div[@class="col-md-12"]/p/text()').get()
		shop['Description'] = desc
		yield shop
		yield scrapy.Request('https://shop.pineapplevictoria.ca/menu/', callback=self.parse_menu)

	def parse_menu(self, response):
		print(response.url)
		product_links = response.xpath('//div[@class="info"]/a/@href').getall()
		for product_link in product_links:
			yield scrapy.Request(product_link, callback=self.parse_products)
		next_page = response.xpath('//li[@class="next enabled"]/a/@href').get()
		if next_page:
			yield scrapy.Request(next_page, callback=self.parse_menu)

	def parse_products(self, response):
		add_link = response.xpath('//form[@id="product_configure_form"]/@action').get()
		product_id = add_link.split('add/')[1][0:-1]
		category = ''
		price = response.xpath('//span[@class="price"]/text()').get().replace('C$', '').rstrip()
		name = response.xpath('//h1[@class="product-page"]/text()').get().strip().rstrip()
		brand_name = response.xpath('//div[@class="tags-actions row"]/div/a/h2/text()').get()
		if not brand_name:
			if '-' in name:
				brand_name = name.split(' - ', 1)[0]
			else:
				brand_name = name.split(' ', 1)[0]
				if brand_name == 'THC':
					brand_name = 'THC Biomed'
		stock = response.xpath('//span[@class="in-stock"]/text()').get()
		if stock.lower().strip().rstrip() == 'in stock':
			stock = 'In Stock'
		else:
			stock = 'Out of Stock'
		img = response.xpath('//div[@class="images"]/a/img[1]/@src').get()
		paragraphs = response.xpath('//div[@class="page info active"]/p/text()').getall()
		desc = ''
		cbd_name = ''
		thc_name = ''
		cbd = ''
		thc = ''
		if paragraphs:
			desc = '\n'.join(paragraphs)
			thc = re.search(r"THC( -|:)? ([0-9\.]+ ?- ?)?[0-9\.]+%", desc)
			if thc:
				thc = thc.group().replace('THC - ', '').replace('THC: ', '')
			else:
				thc = re.search(r"([0-9\.]+-)?[0-9\.]+mg of THC", desc)
				if thc:
					thc = thc.group().replace(' of THC', '')
				else:
					thc = re.search(r"[0-9\.]+mg THC", desc)
					if thc:
						thc = thc.group().replace(' THC', '')
			cbd = re.search(r"CBD( -|:)? ([0-9\.]+ ?- ?)?[0-9\.]+%", desc)
			if cbd:
				cbd = cbd.group().replace('CBD - ', '').replace('CBD: ', '')
			else:
				cbd = re.search(r"([0-9\.]+-)?[0-9\.]+mg of CBD", desc)
				if cbd:
					cbd = cbd.group().replace(' of CBD', '')
				else:
					cbd = re.search(r"[0-9\.]+mg CBD", desc)
					if cbd:
						cbd = cbd.group().replace(' CBD', '')
		if thc:
			thc_name = 'THC'
		if cbd:
			cbd_name = 'CBD'
		qt = re.search(r'quantity = [0-9]+', response.text).group().replace('quantity = ', '')
		yield {
			"Page URL": response.url,
			"Brand": brand_name,
			"Name": name,
			"SKU": '',
			"Out stock status": stock,
			"Stock count": qt,
			"Currency": "CAD",
			"ccc": "",
			"Price": price,
			"Manufacturer": 'Pineapple Express',
			"Main image": img,
			"Description": desc,
			"Product ID": product_id,
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
			"Cat tree 1 parent": category,
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
			"Attribute 1": '',
			"Attribute Value 1": cbd_name,
			"Attribute 2": cbd,
			"Attribute value 2": thc_name,
			"Attribute 3": thc,
			"Attribute value 3": '',
			"Attribute 4": "",
			"Attribute value 4": "",
			"Reviews": '',
			"Review link": "",
			"Rating": '',
			"Address": '',
			"p_id": self.p_id
		}
