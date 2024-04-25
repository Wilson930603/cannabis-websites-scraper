import re

from Independent.spiders.base_spider import BaseSpider
import scrapy


class EvergreenSpider(BaseSpider):
	name = 'ecsvan'
	headers = {
		'cookie': 'age_gate=30'
	}
	p_id = '14764755'

	def start_requests(self):
		url = 'https://ecsvan.ca/'
		yield scrapy.Request(url, headers=self.headers, callback=self.parse)

	def parse(self, response):
		address, additional = response.xpath('//div[@data-id="609d6c2d"]/div/div/p/text()').get().split(', ')
		city, province, postal_code = additional.split(' ', 2)
		postal_code = postal_code.replace('Canada', '').strip().rstrip()
		phone = response.xpath('//div[@data-id="5884acb9"]/div/div/p/text()').get()
		yield {
			"Producer ID": '',
			"p_id": self.p_id,
			"Producer": f"Evergreen Cannabis - {city}",
			"Description": 'At Evergreen we will never try to sell you something that we don’t believe will work for you.  Our expert staff possess a combined experience of over 20 years in the cannabis industry and we are thrilled to share that knowledge with you.  Our products have been carefully curated based on high quality at great prices so you don’t need to waste time and money trying strains that are not a good value for your dollar.',
			"Link": "https://ecsvan.ca/",
			"SKU": "",
			"City": city,
			"Province": province,
			"Store Name": "Evergreen Cannabis",
			"Postal Code": postal_code,
			"long": "",
			"lat": "",
			"ccc": "",
			"Page Url": "https://ecsvan.ca/",
			"Active": "",
			"Main image": "https://i1.wp.com/ecsvan.ca/wp-content/uploads/2019/02/evergreen-logo-header.jpg",
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
			"Email": "info@ecsvan.ca",
			"Social": "https://twitter.com/ecsvan/|https://www.instagram.com/evergreen.van|https://open.spotify.com/user/iygkyn5icib0lignoxrt8rg90",
			"FullAddress": "",
			"Address": address,
			"Additional Info": "",
			"Created": "",
			"Comment": "",
			"Updated": ""
		}
		category_links = response.xpath('//a[contains(@href, "https://ecsvan.ca/ecs-product") and @class="elementor-sub-item" and not(@tabindex)]/@href').getall()[0:-1]
		for category_link in category_links:
			yield scrapy.Request(category_link, callback=self.parse_category, headers=self.headers)

	def parse_category(self, response):
		category_name = response.xpath('//head/title/text()').get().split('–')[0].strip().rstrip()
		sections = response.xpath('//section[contains(@class, "elementor-top-section")]')[7:-1]
		sub_category_name = ''
		for section in sections:
			try:
				new_cat = section.xpath(f'./div/div/div/div/div/div[3]/div/h2[@class="elementor-heading-title elementor-size-default"]/text()').get().strip().rstrip()
				if new_cat in ["sativa flower", "hybrid flower", "indica flower", "CBD flower", "Seeds", "sativa dominant joints", "HYBRID joints", "Indica dominant joints", "high cbd joints", "Gummies", "CHOCOLATE", "DRINKS", "other", "SATIVA 510 VAPE CARTRIDGES", "HYBRID 510 VAPE CARTRIDGES", "INDICA 510 VAPE CARTRIDGES", "CBD 510 VAPE CARTRIDGES", "pax era pods (compatible with pax era only)", "complete 510 vape kits", "Batteries & Devices", "Hash & Kief", "rosin & resin", "shatter, badder, wax, & crumble", "other Concentrates & Extracts", "cbd oil", "balanced cbd/thc oil", "THC oil", "THC & CBD capsules", "Topicals", "Evergreen Branded Merchandise?", "pax premium vaporizers", "pax vaporizer accessories", "concentrate accessories", "smoking accessories", "misc gear"]:
					sub_category_name = new_cat
					continue
			except:
				pass
			products_box = section.xpath(f'./div/div/div/div/div')
			for product_box in products_box:
				img = product_box.xpath('./div//img/@src').get()
				if not img:
					continue
				name = product_box.xpath('./section//h2//text()').get()
				desc = ''
				thc_name = ''
				thc = ''
				cbd_name = ''
				cbd = ''
				weight = ''
				try:
					brand = product_box.xpath('./section//h2//..').get().split('by ')[1].split('<')[0].strip().rstrip().replace('&amp;', '&')
				except:
					brand = ''
				if 'vape' in response.url or 'concentrates' in response.url or 'gear' in response.url:
					pr = product_box.xpath('./div[3]//h2').get()
					if not pr:
						pr = product_box.xpath('./div[4]//h2').get()
					if not pr:
						pr = product_box.xpath('./div[2]//h2').get()
					if '<a' in pr:
						price = pr.split('$')[1].split('<')[0]
						old_price = price
					elif 'By donation' in pr:
						continue
					elif 'Now only' in pr:
						old_price, price = pr.split('<s>')[1].split('</i>')[0].replace('$', '').split('</s>')
						price = price.split(' ')[-1]
					elif '<br>' in pr:
						try:
							weight, price = pr.split('">')[1].split('<br>')[0].replace('$', '').split('-')
							weight = weight.strip().rstrip()
							price = price.strip().rstrip()
							old_price = price
						except:
							try:
								weight, price = pr.split('<br>')[1].replace('$', '').split('-')
								weight = weight.strip().rstrip().split(' ')[0]
								price = price.strip().rstrip()
								old_price = price
							except:
								price = pr.split('$')[1].replace('</h2>', '')
								old_price = price
					elif 'was' in pr:
						weight, price = pr.split('">')[1].split('</h2>')[0].replace('$', '').split('-')
						weight = weight.strip().rstrip()
						old_price, price = price.split('</s>')
						old_price = old_price.split('>')[1]
						price = price.split(' ')[-1]
					else:
						try:
							weight, price = pr.split('">')[-1].split('</')[0].replace('$', '').split('-')
							weight = weight.strip().rstrip()
							price = price.strip().rstrip()
							old_price = price
						except:
							price = pr.split('">')[1].split('</h2>')[0].replace('$', '')
							old_price = ''
							weight = ''
				elif 'edibles' in response.url or 'gear' in response.url:
					pr = product_box.xpath('./div[3]//h2').get()
					if 'Now' in pr:
						weight, price = product_box.xpath('./div[3]//h2').get().split('">')[1].split('</h2>')[0].replace('$', '').split('<br>')
						old_price, price = price.split('</s>')
						old_price = old_price.split('>')[1]
						price = price.split(' ')[-1].split('<')[0]
					else:
						try:
							weight, price = product_box.xpath('./div[3]//h2').get().split('">')[1].split('</h2>')[0].replace('$', '').split('<br>')
							weight = weight.strip().rstrip()
							price = price.strip().rstrip()
							old_price = price
						except:
							weight, price = product_box.xpath('./div[3]//h2').get().split('">')[1].split('</h2>')[0].split('$')
							weight = weight.strip().rstrip()
							price = price.strip().rstrip()
							old_price = price
				else:
					try:
						weight, price = product_box.xpath('./div[2]//h2/text()').get().replace('$', '').split(' - ')
						old_price = price
					except:
						weight, price = product_box.xpath('./div[3]//h2/text()').get().replace('$', '').split(' - ')
						old_price = price
				if sub_category_name != 'Seeds' and 'preroll' not in response.url and 'edibles' not in response.url and 'vape' not in response.url and 'concentrates' not in response.url:
					dsc_tabs = product_box.xpath('./section[2]//div[@class="elementor-text-editor elementor-clearfix"]//text()').getall()
					for dsc_tab in dsc_tabs:
						x = dsc_tab.strip()
						if x:
							if x.startswith('THC: '):
								thc_name, thc = x.split(': ')
							elif x.startswith('CBD: '):
								cbd_name, cbd = x.split(': ')
							else:
								desc += x + '\n'
				else:
					if 'concentrates' in response.url:
						cleanr = re.compile('<.*?>')
						cleantext = re.sub(cleanr, '', product_box.xpath('./section//h2/..').get())
						dsc = cleantext.strip().splitlines()[1:-1]
						for ds in dsc:
							x = ds.strip()
							desc += x + '\n'
						dsc = product_box.xpath('./div[2]//p//text()').getall()
						dsc = ''.join(dsc)
						if dsc.startswith('CBD'):
							cbd_name, cbd = dsc.split(': ', 1)
						else:
							thc_name, thc = dsc.split(': ', 1)
					elif 'edibles' in response.url:
						dsc = product_box.xpath('./section//h2//text()').getall()[1:-1]
						for ds in dsc:
							x = ds.strip()
							desc += x + '\n'
						dsc = product_box.xpath('./div[2]//p//text()').getall()
						for ds in dsc:
							x = ds.strip()
							if x:
								if x.startswith('THC: '):
									if '(' in x:
										thc = x.replace('THC: ', '').split('(')[1].split(')')[0]
									else:
										thc = x.replace('THC: ', '').split(' ')[0]
									thc_name = 'THC'
								elif x.startswith('CBD: '):
									if '(' in x:
										cbd = x.replace('CBD: ', '').split('(')[1].split(')')[0]
									else:
										cbd = x.replace('CBD: ', '').split(' ')[0]
									cbd_name = 'CBD'
					elif 'preroll' in response.url:
						desc = product_box.xpath('./section//h2').get().split('<br>')[1].strip().replace('</h2>', '')
						dsc = product_box.xpath('./div[2]//p//text()').getall()
						for ds in dsc:
							x = ds.strip()
							if x:
								if x.startswith('THC: '):
									thc_name, thc = x.split(':')
								elif x.startswith('CBD: '):
									cbd_name, cbd = x.split(':')
					else:
						dsc = product_box.xpath('./section//h2//text()').getall()[1:-1]
						for ds in dsc:
							x = ds.strip()
							desc += x + '\n'
						dsc = product_box.xpath('./div[2]//p//text()').getall()
						for ds in dsc:
							x = ds.strip()
							if x:
								if x.startswith('THC: '):
									thc_name, thc = x.split(': ')
								elif x.startswith('CBD: '):
									cbd_name, cbd_max = x.split(': ')
				cbd = cbd.replace(' total', '')
				if price == old_price:
					old_price = ''
				thc = thc.strip().rstrip().replace(' ', '')
				cbd = cbd.strip().rstrip().replace(' ', '')
				if 'g' not in thc and '%' not in thc and thc:
					thc = f'{thc}%'
				if 'g' not in cbd and '%' not in cbd and cbd:
					cbd = f'{cbd}%'
				if weight and ' ' in weight:
					weight = weight.split(' ')[0]
				yield {
					"Page URL": response.url,
					"Brand": brand,
					"Name": name,
					"SKU": '',
					"Out stock status": 'In Stock',
					"Stock count": "",
					"Currency": "CAD",
					"ccc": "",
					"Price": price,
					"Manufacturer": '',
					"Main image": img,
					"Description": desc.strip().rstrip(),
					"Product ID": '',
					"Additional Information": '',
					"Meta description": "",
					"Meta title": "",
					"Old Price": old_price,
					"Equivalency Weights": "",
					"Quantity": "",
					"Weight": weight,
					"Option": "",
					"Option type": '',
					"Option Value": "",
					"Option image": "",
					"Option price prefix": "",
					"Cat tree 1 parent": category_name,
					"Cat tree 1 level 1": sub_category_name,
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
					"Attribute 3": '',
					"Attribute value 3": '',
					"Attribute 4": '',
					"Attribute value 4": '',
					"Reviews": '0',
					"Review link": "",
					"Rating": '',
					"Address": '',
					"p_id": self.p_id
				}
