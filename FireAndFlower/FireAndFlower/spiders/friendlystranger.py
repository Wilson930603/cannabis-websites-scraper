import re
from time import sleep

from FireAndFlower.spiders.base_spider import BaseSpider
import scrapy
import requests as r
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options


class FriendlystrangerScraper(BaseSpider):
	name = 'friendlystranger'
	shops = {
		'241028': 'https://friendlystranger.com/stores/ON/burlington-plains-road',
		'241029': 'https://friendlystranger.com/stores/ON/cambridge-franklin-blvd',
		'241031': 'https://friendlystranger.com/stores/ON/dundas-osler-dr',
		'241033': 'https://friendlystranger.com/stores/ON/london-richmond-st',
		'241034': 'https://friendlystranger.com/stores/ON/midland-bay-st',
		'241035': 'https://friendlystranger.com/stores/ON/oshawa-ritson-rd',
		'241036': 'https://friendlystranger.com/stores/ON/toronto-church-st',
		'241037': 'https://friendlystranger.com/stores/ON/toronto-danforth-ave',
		'241038': 'https://friendlystranger.com/stores/ON/toronto-little-italy',
		'241041': 'https://friendlystranger.com/stores/ON/toronto-queen-st-w'
	}
	shop_name = 'Friendly Stranger'
	img = 'https://ca.cdn.hifyreretail.com/130007/20210607/8b01aeb7ba5a4e6c80350d6e0d24809a'
	email = 'info@friendlystranger.com'

	def start_requests(self):
		for shop_pid in self.shops:
			print(shop_pid)
			url = f'https://friendlystranger.com/shop/{shop_pid}?redirect=%2Fshop'
			res = r.get(url)
			cookies = ''
			for cookie in res.cookies:
				cookies += f'{cookie.name}={cookie.value}; '
			yield scrapy.Request(self.shops[shop_pid], headers={'cookie': cookies}, callback=self.parse_store, dont_filter=True, meta={'p_id': shop_pid, 'cookies': cookies})

	def parse_store(self, response):
		p_id = response.meta['p_id']
		cookies = response.meta['cookies']
		full_addr = response.xpath('//div[@class="location-page--address"]/p[1]/text()').getall()
		addr = full_addr[0].strip().rstrip()
		city, province = full_addr[1].strip().rstrip().split(', ')
		postal_code = full_addr[2].strip().rstrip()
		phone = response.xpath('//div[@class="location-page--contact"]/a/text()').get()
		lat, lng = response.xpath('//div[@class="location-page--interactions"]/a/@href').get().split('/')[-1].split(',')
		social = '|'.join(response.xpath('//div[@class="ecom--secondary-footer--grid"]/div[2]/a/@href').getall())
		shop_item = {
			"Producer ID": '',
			"p_id": p_id,
			"Producer": f"{self.shop_name} - {city}",
			"Description": "",
			"Link": response.url,
			"SKU": "",
			"City": city,
			"Province": province,
			"Store Name": self.shop_name,
			"Postal Code": postal_code,
			"long": lng,
			"lat": lat,
			"ccc": "",
			"Page Url": response.url,
			"Active": "",
			"Main image": self.img,
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
			"Email": self.email,
			"Social": social,
			"FullAddress": "",
			"Address": addr,
			"Additional Info": "",
			"Created": "",
			"Comment": "",
			"Updated": ""
		}
		yield shop_item
		all_brands = ["420 Science", "48North", "7ACRES", "Ace Valley", "Arizer", "Avana", "BLK MKT", "Back Forty",
		              "Bhang", "Blendcraft", "Blissed", "Boaz", "Boundless", "Broken Coast", "Canaca",
		              "Canadian Lumber", "CannAccessories", "Cannabolish", "Choice Leaf", "Chowie Wowie",
		              "Citizen Stash", "Color Cannabis", "Cove", "DNA Genetics", "DOJA", "Daily Special", "Divvy",
		              "Dosecann", "Dosist", "EYCE", "Edison", "Eve & Co.", "Everie", "FIGR", "Fire and Flower", "Foray",
		              "GEAR", "Gage", "General Admission", "Generic", "Good Supply", "Hemson Goods", "Houseplant",
		              "Kannastor", "Karma", "King Palm", "Kiwi", "Kolab", "LEVO", "LIT", "Legend", "Little Victory",
		              "Magical Butter", "Mood Ring", "Moose Labs", "OCB", "OGEN", "Orange Chronic", "Original Stash",
		              "PAX", "PULSAR", "Paracanna", "PieceMaker", "Piranha", "Pure Sunfarms", "Quatreau", "Qwest",
		              "RAW", "RYOT", "Randy's", "Red Eye Glass", "Red Eye Tek", "Redecan", "Revity", "Riff", "Saionara",
		              "San Rafael '71", "Sharpstone", "Shine", "Shire Pipe", "Shred", "Simple Stash", "Simply Bare",
		              "Solei", "Spinach", "Studio Briar", "The Wild Florist", "Trailblazer", "Tree of Life", "Twd.",
		              "Tweed", "Up", "Veryvell", "Wana", "West Coast Gifts", "White Rhino", "XMG", "Yocan", "Zig-Zag",
		              "iRie"]
		brands = list(set(all_brands).intersection(self.settings.get('BRANDS', [])))
		brands = '^'.join(brands)
		page = 1
		if brands == '':
			categories = ['Beverages', 'Concentrates', 'Cultivation', 'Edibles', 'Flower', 'Oils', 'Vapes', 'Pre-Rolled', 'Topicals', 'Accessories', 'Apparel']
			for category in categories:
				base_link = f'https://friendlystranger.com/shop?category={category}'
				yield scrapy.Request(base_link, meta={'p_id': p_id, 'cookies': cookies, 'page': page, 'base_link': base_link}, headers={'cookie': cookies}, callback=self.parse_menu, dont_filter=True)
		else:
			base_link = f'https://friendlystranger.com/shop?brand={brands}'
			yield scrapy.Request(base_link, meta={'p_id': p_id, 'cookies': cookies, 'page': page, 'base_link': base_link}, headers={'cookie': cookies}, callback=self.parse_menu, dont_filter=True)

	def parse_menu(self, response):
		print(response.url)
		p_id = response.meta['p_id']
		page = response.meta['page'] + 1
		base_link = response.meta['base_link']
		cookies = response.meta['cookies']
		product_ids = response.xpath('//button[@phx-value-product_id]/@phx-value-product_id').getall()
		print(product_ids)
		for product_id in product_ids:
			yield scrapy.Request(f'https://friendlystranger.com/products/{product_id}', dont_filter=True, callback=self.parse_product, meta={'p_id': p_id, 'product_id': product_id, 'cookies': cookies}, headers={'cookie': cookies})
		if product_ids:
			link = f'{base_link}&page={page}'
			yield scrapy.Request(link, dont_filter=True, callback=self.parse_menu, meta={'p_id': p_id, 'page': page, 'base_link': base_link, 'cookies': cookies}, headers={'cookie': cookies})

	def parse_product(self, response):
		print(response.url)
		brand = ''
		try:
			brand = re.search('var prodBrand =.+', response.text).group(0).split('"')[1]
		except:
			pass
		p_id = response.meta['p_id']
		product_id = response.meta['product_id']
		link = response.url
		name = response.xpath('//div[@class="product-page--title-rating"]/h1/text()').get()
		nb_reviews = response.xpath('//a[@id="review-scroller"]/text()').get()
		if nb_reviews:
			nb_reviews = nb_reviews.replace('Reviews', '').strip().rstrip()
		main_img = response.xpath('//div[@class="image-slideshow--slide-wrapper"]/img[1]/@src').get()
		stock = 'In Stock'
		out_stock = response.xpath('//div[@phx-hook="OtherStoresScroll"]/div/span/b/text()').get()
		stock_count = 0
		if out_stock:
			if 'Sold Out' in out_stock:
				stock = 'Out of Stock'
		else:
			stock_count = response.xpath(
				'//div[@class="stock-message round-corners p-1 d-flex align-c justify-c mt-1 bg-warning-light border-warning"]/span/text()').get()
			if stock_count:
				stock_count = int(stock_count.strip().rstrip().replace('Only ', '').replace(' in stock', ''))
			else:
				stock_count = 10
		old_price = ''
		price = response.xpath('//span[@class="price bold"]/text()').get()
		if price:
			price = price.replace('$', '').strip().rstrip()
		else:
			old_price = response.xpath('//span[@class="price line-through muted regular"]/text()').get().replace('$',
			                                                                                                     '').strip().rstrip()
			price = response.xpath(
				'//p[@class="price bold brand m-0 d-flex fd-column justify-c"]/text()[2]').get().replace('$',
			                                                                                             '').strip().rstrip()
		thc = ''
		cbd = ''
		thc_name = ''
		cbd_name = ''
		boxes = response.xpath('//div[@class="bg-gray-light round-corners p-1 d-flex align-c flex-1"]')
		for box in boxes:
			title = box.xpath('./p/text()').get().strip().rstrip()
			value = box.xpath('./span/text()').get().strip().rstrip()
			if title == 'THC':
				thc_name = 'THC'
				thc = value
			elif title == 'CBD':
				cbd_name = 'CBD'
				cbd = value
		sku = ''
		try:
			sku = re.search('var prodSKU =.+', response.text).group(0).split('"')[1]
		except:
			pass
		rating = ''
		try:
			rating = re.search('var prodRating =.+', response.text).group(0).split('"')[1]
		except:
			pass
		options = response.xpath('//select[@id="product_variation_id"]/option/text()').getall()
		first_option = options[0]
		cols = response.xpath('//li[@class="product-details--list-item"]')
		desc = ''
		for col in cols:
			header = col.xpath('./h3/text()').get()
			if 'DESCRIPTION' in header:
				desc = col.xpath('./p/text()').get()
				if desc:
					desc = desc.strip().rstrip()
				break
		item = {
			"Page URL": link,
			"Brand": brand,
			"Name": name,
			"SKU": sku,
			"Out stock status": stock,
			"Stock count": stock_count,
			"Currency": "CAD",
			"ccc": "",
			"Price": price,
			"Manufacturer": self.shop_name,
			"Main image": main_img,
			"Description": desc,
			"Product ID": product_id,
			"Additional Information": '',
			"Meta description": "",
			"Meta title": "",
			"Old Price": old_price,
			"Equivalency Weights": '',
			"Quantity": "",
			"Weight": first_option,
			"Option": "",
			"Option type": '',
			"Option Value": "",
			"Option image": "",
			"Option price prefix": "",
			"Cat tree 1 parent": "",
			"Cat tree 1 level 1": "",
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
			"Reviews": nb_reviews,
			"Review link": "",
			"Rating": rating,
			"Address": '',
			"p_id": p_id
		}
		if len(options) > 1:
			item['Option type'] = "Choose an option"
			item['Option Value'] = first_option
			item['Option price prefix'] = price
			yield item
			cookies = response.meta['cookies']
			op = Options()
			op.add_argument('no-sandbox')
			op.headless = True
			browser = webdriver.Chrome(options=op)
			browser.get(response.url)
			for cookie in cookies.rstrip()[0:-1].split(';'):
				name, value = cookie.strip().split('=')
				name = name.strip().rstrip()
				flag = False
				if name in ['AWSALBCORS', '_ecom_key']:
					flag = True
				browser.add_cookie(
					{'httpOnly': False, 'name': name, 'value': value, 'domain': 'friendlystranger.com', 'path': '/',
					 'secure': flag})
			browser.get(response.url)
			sleep(5)
			browser.find_element_by_id('age_gate_day').send_keys('2')
			browser.find_element_by_id('age_gate_month').send_keys('1')
			browser.find_element_by_id('age_gate_year').send_keys('1990')
			browser.find_element_by_id('age_gate_year').send_keys(Keys.ENTER)
			sleep(10)
			browser.get(response.url)
			sleep(5)
			try:
				for option in options[1:]:
					item['Option Value'] = option
					item['Weight'] = option
					select = browser.find_element_by_id('product_variation_id')
					browser.execute_script("arguments[0].scrollIntoView();", select)
					select.send_keys(Keys.DOWN)
					sleep(2)
					stock = 'In Stock'
					try:
						out_stock = browser.find_element_by_xpath('//div[@phx-hook="OtherStoresScroll"]/div/span/b')
						if 'Sold Out' in out_stock.get_attribute('innerText'):
							stock = 'Out of Stock'
					except:
						pass
					stock_count = 0
					if stock == 'In Stock':
						try:
							stock_count = browser.find_element_by_xpath(
								'//div[@class="stock-message round-corners p-1 d-flex align-c justify-c mt-1 bg-warning-light border-warning"]/span')
							stock_count = int(
								stock_count.get_attribute('innerText').strip().rstrip().replace('Only ', '').replace(
									' in stock', ''))
						except:
							stock_count = 10
					item['Out stock status'] = stock
					item['Stock count'] = stock_count
					try:
						price = browser.find_element_by_xpath('//span[@class="price bold"]')
						price = price.get_attribute('innerText').replace('$', '')
						item['Option price prefix'] = price
						item['Price'] = price
					except:
						n, price, old_price = browser.find_element_by_xpath(
							'//p[@class="price bold brand m-0 d-flex fd-column justify-c"]').get_attribute(
							'innerText').split('$')
						price = price.strip().rstrip()
						old_price = old_price.strip().rstrip()
						item['Option price prefix'] = price
						item['Price'] = price
						item['Old Price'] = old_price
					yield item
				try:
					browser.execute_script("window.onunload = null; window.onbeforeunload=null")
				finally:
					pass
				browser.close()
				browser.quit()
			except:
				browser.close()
				browser.quit()
		else:
			yield item
