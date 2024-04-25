from Independent.spiders.base_spider import BaseSpider
import scrapy
import json
import re


class OriginalfarmSpider(BaseSpider):
	name = 'originalfarm'
	headers = {
		'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36',
		'cookie': 'age_gate=56',
	}
	locations = {
		'downtownvictoria': '63708554',
		'duncan': '63708555',
		'hillsidevictoria': '63708556',
		'langford': '63708557'
	}

	def start_requests(self):
		yield scrapy.Request(f'https://originalfarm.com/locations/', callback=self.parse_location, headers=self.headers)

	def parse_location(self, response):
		shops_data = json.loads(response.xpath('//@data-locations').get())
		boxes = response.xpath('//div[@class="et_pb_text_inner"]')[:-1]
		for box in boxes:
			ind = ''
			farm = box.xpath('./h3[1]/text()').get().lower()
			if 'duncan' in farm:
				ind = 1
			elif 'langford' in farm:
				ind = 3
			elif 'hillside' in farm:
				ind = 2
			elif 'downtown' in farm:
				ind = 0
			desc = ' '.join(box.xpath('./p[1]//text()').getall())
			phones = box.xpath('./p[3]//a/@href').getall()
			phone = box.xpath('./p[3]//text()').get().split(': ', 1)[-1]
			if len(phones) == 2:
				phone = phones[0].split('tel:')[1]
			yield {
				"Producer ID": '',
				"p_id": self.locations[shops_data[ind]['slug']],
				"Producer": f"Original Farms - {shops_data[ind]['name']}",
				"Description": desc,
				"Link": shops_data[ind]['home_page_url'],
				"SKU": "",
				"City": shops_data[ind]['city'],
				"Province": shops_data[ind]['province'],
				"Store Name": "Original Farms",
				"Postal Code": shops_data[ind]['postal_code'],
				"long": shops_data[ind]['lng'],
				"lat": shops_data[ind]['lat'],
				"ccc": "",
				"Page Url": shops_data[ind]['home_page_url'],
				"Active": "",
				"Main image": shops_data[ind]['image_url'],
				"Image 2": shops_data[ind]['image_thumb_url'],
				"Image 3": shops_data[ind]['image_medium_url'],
				"Image 4": '',
				"Image 5": '',
				"Type": "",
				"License Type": "",
				"Date Licensed": "",
				"Phone": shops_data[ind]['phone'],
				"Phone 2": phone,
				"Contact Name": "",
				"EmailPrivate": "",
				"Email": shops_data[ind]['email'],
				"Social": '',
				"FullAddress": "",
				"Address": shops_data[ind]['line_1'],
				"Additional Info": "",
				"Created": "",
				"Comment": "",
				"Updated": ""
			}
		yield scrapy.Request('https://originalfarm.com/wp-json/wp/v3/menu-products?per_page=1000&in_stock=true&page=1&category_slug=&remove_out_stock_variation=false&vendor_id=&orderby=alpha_asc&filter_vendor=NaN&filter_sale_items=false&filter_clearance_items=false&filter_new_items=false&order=asc', headers=self.headers, callback=self.parse_products)

	def parse_products(self, response):
		for product in response.json():
			brand = product["vendor_name"]
			dsc = product["description"]
			if dsc:
				dsc = dsc.rstrip()
			item = {
				"Page URL": f'https://originalfarm.com/menu/#products/{product["slug"]}',
				"Brand": product["vendor_name"],
				"Name": product["title"],
				"SKU": "",
				"Out stock status": "",
				"Stock count": "",
				"Currency": "CAD",
				"ccc": "",
				"Price": product["price"],
				"Manufacturer": '',
				"Main image": product['images'][0]['large_url'] if 'images' in product and len(product['images']) > 0 else '',
				"Description": dsc,
				"Product ID": product["id"],
				"Additional Information": '',
				"Meta description": "",
				"Meta title": "",
				"Old Price": "",
				"Equivalency Weights": "",
				"Quantity": "",
				"Weight": "",
				"Option": "",
				"Option type": '',
				"Option Value": "",
				"Option image": "",
				"Option price prefix": "",
				"Cat tree 1 parent": "",
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
				"Attribute 1": "",
				"Attribute value 1": "",
				"Attribute 2": "",
				"Attribute value 2": "",
				"Attribute 3": "",
				"Attribute value 3": "",
				"Attribute 4": "",
				"Attribute value 4": "",
				"Reviews": '',
				"Review link": "",
				"Rating": '',
				"Address": '',
				"p_id": ''
			}
			if item["Attribute value 1"] == "":
				try:
					item["Attribute value 1"] = \
					re.search('CBD: [^ \n]+', item["Description"]).group().replace('\\/', '/').split(': ')[1]
				except:
					pass
			if item["Attribute value 2"] == "":
				try:
					item["Attribute value 2"] = \
					re.search('THC: [^ \n]+', item["Description"]).group().replace('\\/', '/').split(': ')[1]
				except:
					pass
			has_variants = len(product["variants"]) != 1
			on_sale = product["on_sale"]
			if not has_variants:
				variant = product["variants"][0]
				item["Cat tree 1 parent"] = variant["category_id_pos"]
				item["Cat tree 1 level 1"] = variant["sub_category_id_pos"]
				if on_sale:
					item["Old Price"] = variant["price"]
					item["Price"] = variant["sale_price"]
				weight = variant["weight"]
				if weight == '0.00':
					weight = ''
				else:
					weight = f'{weight}g'
				item["Weight"] = weight
				for location in variant["locations"]:
					item["p_id"] = self.locations[location["slug"]]
					if not item["Attribute value 1"]:
						if location["potency_min_cbd"] == location["potency_max_cbd"]:
							item["Attribute value 1"] = location["potency_min_cbd"]
						else:
							item["Attribute value 1"] = f'{location["potency_min_cbd"]}-{location["potency_max_cbd"]}'
						if item["Attribute value 1"] == '0.00':
							item["Attribute value 1"] = ''
						else:
							if location["potency_mg_pct"] == "P":
								item["Attribute value 1"] = f'{item["Attribute value 1"]}%'
							else:
								item["Attribute value 1"] = f'{item["Attribute value 1"]}mg/g'
					if not item["Attribute value 2"]:
						if location["potency_min_thc"] == location["potency_max_thc"]:
							item["Attribute value 2"] = location["potency_min_thc"]
						else:
							item["Attribute value 2"] = f'{location["potency_min_thc"]}-{location["potency_max_thc"]}'
						if item["Attribute value 2"] == '0.00':
							item["Attribute value 2"] = ''
						else:
							if location["potency_mg_pct"] == "P":
								item["Attribute value 2"] = f'{item["Attribute value 2"]}%'
							else:
								item["Attribute value 2"] = f'{item["Attribute value 2"]}mg/g'
					item["Stock count"] = location["quantity"]
					if location["out_of_stock_at_selected_location"]:
						item["Out stock status"] = "Out of Stock"
					else:
						item["Out stock status"] = "In Stock"
					if item["Attribute value 1"]:
						item["Attribute 1"] = 'CBD'
					if item["Attribute value 2"]:
						item["Attribute 2"] = 'THC'
					yield item
			else:
				variant = product["variants"][0]
				item["Cat tree 1 parent"] = variant["category_id_pos"]
				if on_sale:
					item["Old Price"] = variant["price"]
					item["Price"] = variant["sale_price"]
				for variant in product["variants"]:
					weight = variant["weight"]
					if weight == '0.00':
						weight = ''
					else:
						weight = f'{weight}g'
					item["Weight"] = weight
					if variant["on_sale"]:
						item["Option price prefix"] = variant["sale_price"]
					else:
						item["Option price prefix"] = variant["price"]
					item["Price"] = item["Option price prefix"]
					item["Option type"] = "Choose a Size"
					item["Option Value"] = variant["quantity"]
					for location in variant["locations"]:
						item["p_id"] = self.locations[location["slug"]]
						item["Stock count"] = location["quantity"]
						if not item["Attribute value 1"]:
							if location["potency_min_cbd"] == location["potency_max_cbd"]:
								item["Attribute value 1"] = location["potency_min_cbd"]
							else:
								item[
									"Attribute value 1"] = f'{location["potency_min_cbd"]}-{location["potency_max_cbd"]}'
							if item["Attribute value 1"] == '0.00':
								item["Attribute value 1"] = ''
							else:
								if location["potency_mg_pct"] == "P":
									item["Attribute value 1"] = f'{item["Attribute value 1"]}%'
								else:
									item["Attribute value 1"] = f'{item["Attribute value 1"]}mg/g'
						if not item["Attribute value 2"]:
							if location["potency_min_thc"] == location["potency_max_thc"]:
								item["Attribute value 2"] = location["potency_min_thc"]
							else:
								item[
									"Attribute value 2"] = f'{location["potency_min_thc"]}-{location["potency_max_thc"]}'
							if item["Attribute value 2"] == '0.00':
								item["Attribute value 2"] = ''
							else:
								if location["potency_mg_pct"] == "P":
									item["Attribute value 2"] = f'{item["Attribute value 2"]}%'
								else:
									item["Attribute value 2"] = f'{item["Attribute value 2"]}mg/g'
						if location["out_of_stock_at_selected_location"]:
							item["Out stock status"] = "Out of Stock"
						else:
							item["Out stock status"] = "In Stock"
						if item["Attribute value 1"]:
							item["Attribute 1"] = 'CBD'
						if item["Attribute value 2"]:
							item["Attribute 2"] = 'THC'
						yield item
