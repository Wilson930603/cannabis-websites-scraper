from Independent.spiders.base_spider import BaseSpider
import scrapy
import re


class GreenerycannabisScraper(BaseSpider):
	name = 'greenerycannabis'
	start_urls = ['https://greenerycannabisboutique.ca/clickncollect/contact']
	shop_name = 'Greenery Cannabis Boutique'
	basic_id = 27698159

	def parse(self, response):
		boxes = response.xpath('//div[@class="row_col_wrap_12_inner col span_12  left"]/div')
		for box in boxes:
			all_address = box.xpath('.//p/text()').getall()
			address = all_address[0]
			city, pro_zip = all_address[1].strip().rstrip().split(', ')
			province, postal_code = pro_zip.split(' ', )
			postal_code = postal_code.split(' ', 1)[1]
			phone = box.xpath('.//h2/a/text()').get().replace('-', ' ')
			social = '|'.join(response.xpath('//a[@target="_blank" and contains(@href, "http")]/@href').getall())
			main_image = response.xpath('//a[@class="logo"]/img/@src').get()
			p_id = self.basic_id
			self.basic_id += 1
			yield {
				"Producer ID": '',
				"p_id": p_id,
				"Producer": f'{self.shop_name} - {city}',
				"Description": "",
				"Link": "https://greenerycannabisboutique.ca/",
				"SKU": "",
				"City": city,
				"Province": province,
				"Store Name": self.shop_name,
				"Postal Code": postal_code,
				"long": "",
				"lat": "",
				"ccc": "",
				"Page Url": "https://greenerycannabisboutique.ca/",
				"Active": "",
				"Main image": f'https://greenerycannabisboutique.ca{main_image}',
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
				"Social": social,
				"FullAddress": "",
				"Address": address,
				"Additional Info": "",
				"Created": "",
				"Comment": "",
				"Updated": ""
			}
		headers = {
			'cookie': f'store_id=13; store_limit=30.00; store_state=British%20Columbia; store_city=Salmon%20Arm'}
		yield scrapy.Request('https://greenerycannabisboutique.ca/ht/api/objects/kiosk/main_products?on_hand=true&cannabis=true&is_active=true&thumbnails=true&page_size=9000&page=0&onsale=0&favorites=0&newproducts=0&featured=0&sativa=false&hybrid=false&indica=false', headers=headers, callback=self.parse_products)

	def parse_products(self, response):
		products = response.json()
		for product in products:
			brand = product["brand_name"]
			if not brand:
				brand = ''
			thc = ''
			cbd = ''
			unit = product['test_units']
			if not product["test_thc"]:
				thc = '0.00%'
			else:
				if product["test_thc"] == '0.000':
					thc = '0.00%'
				else:
					thc_min = str(round(float(product["test_thc"]), 2))
					thc = f'{thc_min}{unit}'
			if not product["test_cbd"]:
				cbd = '0.00%'
			else:
				if product["test_cbd"] == '0.000':
					cbd = '0.00%'
				else:
					cbd_min = str(round(float(product["test_cbd"]), 2))
					cbd = f'{cbd_min}{unit}'
			img = product["main_image"]
			if img:
				img = f'https://greenerycannabisboutique.ca{img}'
			desc = product['product_info']
			if desc:
				desc = desc.strip().rstrip()
				cleaner = re.compile('<.*?>')
				desc = re.sub(cleaner, '', desc)
				desc = re.sub(re.compile('\n+'), '\n', desc)
			eq = product["mj_grams"]
			if eq:
				eq = round(float(eq), 2)
			else:
				eq = '0.00'
			weight = product['uom']
			if not weight:
				weight = ''
			cnt = ''
			stock = 'Out of Stock'
			if product["on_hand"]:
				cnt = int(float(product["on_hand"]))
				if cnt < 0:
					cnt = 0
				if cnt > 0:
					stock = 'In Stock'
			yield {
				"Page URL": f'https://greenerycannabisboutique.ca/clickncollect/shop-cannabis-online/salmon_arm/{product["id"]}',
				"Brand": brand,
				"Name": product["description"],
				"SKU": product['pid'],
				"Out stock status": stock,
				"Stock count": cnt,
				"Currency": "CAD",
				"ccc": "",
				"Price": round(float(product['price']), 2),
				"Manufacturer": self.shop_name,
				"Main image": img,
				"Description": desc,
				"Product ID": product['id'],
				"Additional Information": '',
				"Meta description": "",
				"Meta title": "",
				"Old Price": '',
				"Equivalency Weights": f'{eq}g of Cannabis',
				"Quantity": "",
				"Weight": weight,
				"Option": "",
				"Option type": '',
				"Option Value": "",
				"Option image": "",
				"Option price prefix": "",
				"Cat tree 1 parent": product["category_name"],
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
				"Attribute 1": "CBD",
				"Attribute Value 1": cbd,
				"Attribute 2": "THC",
				"Attribute value 2": thc,
				"Attribute 3": "",
				"Attribute value 3": "",
				"Attribute 4": "",
				"Attribute value 4": "",
				"Reviews": '',
				"Review link": "",
				"Rating": '',
				"Address": '',
				"p_id": 27698160
			}
