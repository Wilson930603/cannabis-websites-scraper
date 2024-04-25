from Independent.spiders.base_spider import BaseSpider
import scrapy


class BudExpressSpider(BaseSpider):
	name = 'budexpress'
	start_urls = ['https://budexpress.com/pages/content-page']
	page = 1
	p_id = 472698113
	shop_name = 'Bud Express Co.'

	def parse(self, response):
		desc = '\n'.join(response.xpath('//div[@class="page-wrap page-content"]/div[@class="container"]/p/span/text()').getall())
		contact = response.xpath('//div[@id="footer-links"]/div/div[3]/div/a/text()').getall()
		phone = contact[0].split(': ')[1].replace('-', ' ')
		addr, city = contact[3].split(', ')
		email = contact[4]
		img = response.xpath('//img[@alt="brand-logo"]/@src').get()
		yield {
			"Producer ID": '',
			"p_id": self.p_id,
			"Producer": f"{self.shop_name} - {city}",
			"Description": desc,
			"Link": 'https://budexpress.com/',
			"SKU": "",
			"City": city,
			"Province": 'Ontario',
			"Store Name": self.shop_name,
			"Postal Code": 'M6J 1E5',
			"long": '-79.40697569999999',
			"lat": '43.6467528',
			"ccc": "",
			"Page Url": 'https://budexpress.com/',
			"Active": "",
			"Main image": f'https:{img}',
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
			"Address": addr,
			"Additional Info": "",
			"Created": "",
			"Comment": "",
			"Updated": ""
		}
		yield scrapy.Request(f'https://budexpress.com/collections/all?page={self.page}&view=json', callback=self.parse_menu)

	def parse_menu(self, response):
		products = response.json()[0]["products"]
		for product in products:
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
			product_name = product['title']
			if product_name.startswith('- - '):
				product_name = product_name.replace('- - ', '')
			if product_name.startswith('-'):
				product_name = product_name[1:]
			item = {
				"Page URL": f"https://budexpress.com/products/{product['handle']}",
				"Brand": product['vendor'].replace('-', ''),
				"Name": product_name,
				"SKU": '',
				"Out stock status": '',
				"Stock count": "",
				"Currency": "CAD",
				"ccc": "",
				"Price": '',
				"Manufacturer": self.shop_name,
				"Main image": product['media'][0]['src'],
				"Description": product['description'] if product['description'] else '',
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
				price = variant['price']/100
				item['Price'] = price
				if nb_variants > 1:
					item["Option type"] = "Choose a size"
					item["Option Value"] = variant['title']
					item["Option price prefix"] = price
				yield item
		if products:
			self.page += 1
			yield scrapy.Request(f'https://budexpress.com/collections/all?page={self.page}&view=json', callback=self.parse_menu)
