from Independent.spiders.base_spider import BaseSpider
import scrapy
import re


class PrairieRootsSpider(BaseSpider):
	name = 'prairieroots'
	start_urls = ['https://prairieroots.com/']
	shop_name = 'Prairie Roots Cannabis'
	p_id = 682693110
	headers = {
		'cookie': 'PHPSESSID=4nc5cte4r6aqit3r5lea6mi227; PrestaShop-5df70f39fc995706f2efef5709938fd1=def50200046f7e4756a8db53a566333aa4dd609b4730930104fab4d7f56f3c6bf2cd1b6ef6b9ea3fd9208254747c4c4ad250d2bbc2e67b363b69778ebfee0cee77309f6cc168c0058d56da4dec12c05f39e710b4a827289b8aae090a4b7f4986b06942ec1bfcfb0b798f3fc68633e4e187f65bc2bff5cf8d2b93c44847e7c1d8feb5b63ea3cef16282738ae3d0f22bb911fdb405bb05975d8602304a6a9e018ba21afd9a654d7bffe648b0834ab6784fdba8cc0e2583440436cbb84567890054a747f5c707713ee1fbaf7f'
	}

	def parse(self, response):
		desc = '\n'.join(response.xpath('//div[@class="elementor-text-editor rte-content"]/p/text()').getall()[2:])
		img = 'https://prairieroots.com' + response.xpath('//div[@id="desktop_logo"]/a/img/@src').get()
		contacts = response.xpath('//div[@class="contact-rich"]/div/div[contains(@class, "data")]//text()').getall()
		addr = contacts[0].strip().rstrip()
		phone = contacts[2].strip().rstrip().replace('-', ' ')
		email = contacts[5]
		social = response.xpath('//li[@class="instagram"]/a/@href').get()
		city = 'Fort Mill'
		yield {
			"Producer ID": '',
			"p_id": self.p_id,
			"Producer": f"{self.shop_name} - {city}",
			"Description": desc,
			"Link": 'https://prairieroots.com/',
			"SKU": "",
			"City": city,
			"Province": 'SC',
			"Store Name": self.shop_name,
			"Postal Code": '29715',
			"long": '',
			"lat": '',
			"ccc": "",
			"Page Url": 'https://prairieroots.com/',
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
		yield scrapy.Request('https://prairieroots.com/2-all-products?s_day=01&s_month=01&s_year=1986&enter=Enter&order=product.price.desc&resultsPerPage=9999999', callback=self.parse_menu, headers=self.headers)

	def parse_menu(self, response):
		products = response.xpath('//div[@class="thumbnail-container"]/a[1]/@href').getall()
		for product_link in products:
			yield scrapy.Request(product_link, callback=self.parse_product)

	def parse_product(self, response):
		url = response.url
		print(url)
		product = eval(response.xpath('//div[@id="product-details"]/@data-product').get().replace('false', 'False').replace('true', 'True').replace('null', 'None'))
		try:
			img = product['images'][0]['large']['url'].replace('\\/', '/')
		except:
			img = ''
		desc = product['description_short']
		if desc:
			desc = desc.strip().rstrip()
			cleanr = re.compile('<.*?>')
			desc = re.sub(cleanr, '', desc)
		yield {
			"Page URL": url,
			"Brand": '',
			"Name": product['name'],
			"SKU": '',
			"Out stock status": "In stock" if product['quantity'] > 0 else 'Out of Stock',
			"Stock count": product['quantity'],
			"Currency": "CAD",
			"ccc": "",
			"Price": product['price_amount'],
			"Manufacturer": self.shop_name,
			"Main image": img,
			"Description": desc,
			"Product ID": product['id'],
			"Additional Information": "",
			"Meta description": "",
			"Meta title": "",
			"Old Price": '' if product['price_amount'] == product['price_without_reduction'] or not product['price_without_reduction'] else product['price_without_reduction'],
			"Equivalency Weights": "",
			"Quantity": '',
			"Weight": '',
			"Option": "",
			"Option type": "",
			"Option Value": "",
			"Option image": "",
			"Option price prefix": "",
			"Cat tree 1 parent": product['category_name'] if product['category_name'] else '',
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
			"Attribute 1": '',
			"Attribute Value 1": '',
			"Attribute 2": '',
			"Attribute value 2": '',
			"Attribute 3": "",
			"Attribute value 3": '',
			"Attribute 4": "",
			"Attribute value 4": "",
			"Reviews": '',
			"Review link": "",
			"Rating": product['rate'],
			"Address": '',
			"p_id": self.p_id
		}
