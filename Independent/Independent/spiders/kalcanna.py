import re
from Independent.spiders.base_spider import BaseSpider
import scrapy


class KalamalkaScraper(BaseSpider):
	name = 'kalcanna'
	start_urls = ['https://shop.kalcanna.com/ht/api/objects/kiosk/stores']
	store_id = '187369873'

	def parse(self, response):
		store = response.json()[0]
		yield {
			"Producer ID": '',
			"p_id": self.store_id,
			"Producer": f'KALAMALKA CANNABIS - {store["city"]}',
			"Description": "",
			"Link": "https://shop.kalcanna.com/clickncollect/",
			"SKU": "",
			"City": store["city"],
			"Province": store["state"],
			"Store Name": "KALAMALKA CANNABIS",
			"Postal Code": store["zip_code"],
			"long": "",
			"lat": "",
			"ccc": "",
			"Page Url": "https://shop.kalcanna.com/clickncollect/",
			"Active": "",
			"Main image": f'https://shop.kalcanna.com/s/{store["logo"]}',
			"Image 2": '',
			"Image 3": '',
			"Image 4": '',
			"Image 5": '',
			"Type": "",
			"License Type": "",
			"Date Licensed": "",
			"Phone": store["phone"],
			"Phone 2": "",
			"Contact Name": "",
			"EmailPrivate": "",
			"Email": store["email"],
			"Social": "",
			"FullAddress": "",
			"Address": store["address"],
			"Additional Info": "",
			"Created": "",
			"Comment": "",
			"Updated": ""
		}
		headers = {'cookie': f'store_id={store["store_id"]}; store_limit={store["cannabis_limit"]}; store_state={store["state"]}; store_city={store["city"]}'}
		yield scrapy.Request('https://shop.kalcanna.com/ht/api/objects/kiosk/products?page_size=2000&page=0', headers=headers, callback=self.parse_products)

	def parse_products(self, response):
		products = response.json()
		for product in products:
			brand = product["brand_name"]
			if not brand:
				brand = ''
			thc = ''
			cbd = ''
			unit = product['test_units']
			if not product["test_thc_min"] or not product["test_thc_max"]:
				thc = '0.00%'
			else:
				if product["test_thc_max"] == '0.000':
					thc = '0.00%'
				else:
					thc_min = str(round(float(product["test_thc_min"]), 2))
					thc_max = str(round(float(product["test_thc_max"]), 2))
					if thc_min == '0.0':
						if thc_max != '0.0':
							thc = f'{thc_max}{unit}'
						else:
							thc = '0.00%'
					else:
						thc = f'{thc_min}-{thc_max}{unit}'
			if not product["test_cbd_min"] or not product["test_cbd_max"]:
				cbd = '0.00%'
			else:
				if product["test_cbd_max"] == '0.000':
					cbd = '0.00%'
				else:
					cbd_min = str(round(float(product["test_cbd_min"]), 2))
					cbd_max = str(round(float(product["test_cbd_max"]), 2))
					if cbd_min == '0.0':
						if cbd_max != '0.0':
							cbd = f'{cbd_max}{unit}'
						else:
							cbd = '0.00%'
					else:
						cbd = f'{cbd_min}-{cbd_max}{unit}'
			img = product["main_image"]
			if img:
				img = f'https://shop.kalcanna.com{img}'
			desc = product['product_info']
			if desc:
				desc = desc.strip().rstrip()
				cleaner = re.compile('<.*?>')
				desc = re.sub(cleaner, '', desc)
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
				"Page URL": f'https://shop.kalcanna.com/clickncollect/shop-cannabis-online/british_columbia/{product["id"]}',
				"Brand": brand,
				"Name": product["description"],
				"SKU": product['pid'],
				"Out stock status": stock,
				"Stock count": cnt,
				"Currency": "CAD",
				"ccc": "",
				"Price": round(float(product['price']), 2),
				"Manufacturer": '',
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
				"p_id": self.store_id
			}
