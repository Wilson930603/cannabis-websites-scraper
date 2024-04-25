from Independent.spiders.base_spider import BaseSpider
import scrapy


class LakeviewSpider(BaseSpider):
	name = 'lakeview'
	shop_name = 'Lakeview Cannabis'
	allowed_domains = ['lakeviewcannabis.ca']
	start_urls = ['https://www.lakeviewcannabis.ca/contact-us/']
	p_id = '990025'
	
	def parse(self, response):
		address = '4 Mimico Ave, Etobicoke'
		email = 'info@lakeviewcannabis.ca '
		phone = '416 253 5253'
		img = 'http://www.lakeviewcannabis.ca/wp-content/uploads/2020/12/rsz_lv_final.png'
		yield {
			"Producer ID": '',
			"p_id": self.p_id,
			"Producer": f"{self.shop_name}",
			"Description": "",
			"Link": 'http://www.lakeviewcannabis.ca',
			"SKU": "",
			"City": 'Toronto',
			"Province": 'Ontario',
			"Store Name": self.shop_name,
			"Postal Code": 'M8V 1P9',
			"long": '',
			"lat": '',
			"ccc": "",
			"Page Url": response.url,
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
			"Social": "",
			"FullAddress": address,
			"Address": '',
			"Additional Info": "",
			"Created": "",
			"Comment": "",
			"Updated": ""
		}
		for url in response.xpath('//a[@class="nav-top-link"]/@href').getall():
			yield scrapy.Request(url, callback=self.parse_flowers, dont_filter=True)
	
	def parse_flowers(self, response):
		for product in response.xpath('//div[contains(@class, "products")]/div[contains(@class, "product")]'):
			url = product.xpath('.//a/@href').get()
			yield scrapy.Request(url, callback=self.parse_product, dont_filter=True)
		nextPage = response.xpath('//a[contains(@class, "next page-number")]/@href').get()
		if nextPage:
			yield scrapy.Request(nextPage, callback=self.parse_flowers, dont_filter=True)
	
	def parse_product(self, response):
		print(response.url)
		name = response.xpath('//h1/text()').get().strip()
		sku = response.xpath('//span[@class="sku"]/text()').get().split('_')[0]
		try:
			weight = response.xpath('//span[@class="sku"]/text()').get().split('_')[1]
		except:
			weight = ''
		stock = response.xpath('//p[contains(@class, "stock")]/text()').getall()[-1]
		stock_count = response.xpath('//input[contains(@class, "qty")]/@max').get()
		sale_price = response.xpath('//p[contains(@class, "price-on-sale")]/text()')
		if len(sale_price) == 0:
			price = response.xpath('//p[@class="price product-page-price "]/span/bdi/text()').get()
			oldprice = ''
		else:
			oldprice = response.xpath('//p[contains(@class, "price-on-sale")]/del/span/bdi/text()').get()
			price = response.xpath('//p[contains(@class, "price-on-sale")]/ins/span/bdi/text()').get()
		image = response.xpath('//img[contains(@class, "wp-post-image")]/@src').get()
		desc = response.xpath('//div[@id="tab-description"]/p/text()').get()
		try:
			desc = desc.replace('\n', ' ')
		except:
			pass
		product_id = response.xpath('//button[@class="single_add_to_cart_button button alt"]/@value').get()
		thc = cbd = brand = cbd_name = thc_name = ''
		try:
			attributes = response.xpath('//div[@class="product-short-description"]/p/text()').get().split(' | ')
			for item in attributes:
				if 'THC' in item:
					thc = item.replace('THC:', '').strip()
					thc_name = 'THC'
				elif 'CBD' in item:
					cbd = item.replace('CBD:', '').strip()
					cbd_name = 'CBD'
				else:
					brand = item.strip()
		except:
			pass
		name = name.replace('–', '-')
		if '-' in name:
			brand2 = name.split('-')[0]
			if brand.lower() != brand2.lower():
				brand = brand2
		
		reviews = response.xpath('//li[@id="tab-title-reviews"]/a/text()').get().strip().split('(')[1].split(')')[0]
		reviews_link = response.url + '#tab-reviews' if reviews != '0' else ''
		qty = response.xpath('//input[contains(@class, "qty")]/@min').get()
		category = response.xpath('//li[contains(@class, "current-product-ancestor")]//text()').get()

		yield {
			"Page URL": response.url,
			"Brand": brand,
			"Name": name,
			"SKU": sku.replace('"', ''),
			"Out stock status": stock,
			"Stock count": stock_count,
			"Currency": "CAD",
			"ccc": "",
			"Price": price,
			"Manufacturer": self.shop_name,
			"Main image": image,
			"Description": desc,
			"Product ID": product_id,
			"Additional Information": '',
			"Meta description": "",
			"Meta title": "",
			"Old Price": oldprice,
			"Equivalency Weights": '',
			"Quantity": qty,
			"Weight": weight,
			"Option": "",
			"Option type": '',
			"Option Value": "",
			"Option image": "",
			"Option price prefix": "",
			"Cat tree 1 parent": category,
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
			"Reviews": reviews,
			"Review link": reviews_link,
			"Rating": '',
			"Address": '',
			"p_id": self.p_id
		}
