from Independent.spiders.base_spider import BaseSpider
import scrapy


class OneEyesWeederySpider(BaseSpider):
	name = 'oneeyesweedery'
	shop_name = "One Eye's Weedery"
	start_urls = ['https://www.oneeyesweedery.com/shop/products']
	p_id = 52970311

	def parse(self, response):
		yield {
			"Producer ID": '',
			"p_id": self.p_id,
			"Producer": f"{self.shop_name} - Outlook",
			"Description": '',
			"Link": 'https://www.oneeyesweedery.com/',
			"SKU": "",
			"City": 'Outlook',
			"Province": 'SK',
			"Store Name": self.shop_name,
			"Postal Code": 'S0L 2N0',
			"long": '',
			"lat": '',
			"ccc": "",
			"Page Url": 'https://www.oneeyesweedery.com/',
			"Active": "",
			"Main image": 'https://www.oneeyesweedery.com/svg/secondary.svg',
			"Image 2": "",
			"Image 3": "",
			"Image 4": '',
			"Image 5": '',
			"Type": "",
			"License Type": "",
			"Date Licensed": "",
			"Phone": '306 867 9105',
			"Phone 2": "",
			"Contact Name": "",
			"EmailPrivate": "",
			"Email": 'info@oneeyesweedery.com',
			"Social": 'https://www.facebook.com/oneeyesweedery|https://www.instagram.com/oneeyesweedery',
			"FullAddress": "",
			"Address": '221 Franklin Street',
			"Additional Info": "",
			"Created": "",
			"Comment": "",
			"Updated": ""
		}
		products = response.json()
		for product in products:
			cbd_name = ''
			cbd = product['avg_cbd']
			if cbd:
				cbd = f'{cbd}%'
				cbd_name = 'CBD'
			thc_name = ''
			thc = product['avg_thc']
			if thc:
				thc = f'{thc}%'
				thc_name = 'THC'
			item = {
				"Page URL": f"https://www.oneeyesweedery.com/product/{product['slug']}",
				"Brand": product['supplier_name'],
				"Name": product['name'],
				"SKU": product['sku'],
				"Out stock status": '',
				"Stock count": "",
				"Currency": "CAD",
				"ccc": "",
				"Price": '',
				"Manufacturer": self.shop_name,
				"Main image": product['hero_shot_url'],
				"Description": product['long_description'],
				"Product ID": product['id'],
				"Additional Information": "",
				"Meta description": "",
				"Meta title": "",
				"Old Price": '',
				"Equivalency Weights": "",
				"Quantity": '',
				"Weight": '',
				"Option": "",
				"Option type": "",
				"Option Value": "",
				"Option image": "",
				"Option price prefix": "",
				"Cat tree 1 parent": product['product_category']['name'],
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
			nb_variants = len(product['product_variations'])
			for variant in product['product_variations']:
				item['Stock count'] = variant['quantity']
				in_stock = 'Out of Stock'
				if variant['quantity'] > 0:
					in_stock = 'In Stock'
				item['Out stock status'] = in_stock
				price = variant['price']
				item['Price'] = price
				weight = variant['weight_grams']
				item['Weight'] = ''
				if weight != 0:
					item['Weight'] = weight
				if nb_variants > 1:
					item["Option type"] = "Choose a size"
					item["Option Value"] = variant['name']
					item["Option price prefix"] = price
				yield item
