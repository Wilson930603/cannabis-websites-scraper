from FireAndFlower.spiders.base_spider import BaseSpider
import scrapy


class BluntAndCherrySpider(BaseSpider):
	name = 'bluntandcherry'
	shop_name = 'Blunt & Cherry'
	p_id = 38610937

	headers = {
		'authority': 'bluntandcherry.ca',
		'cache-control': 'max-age=0',
		'sec-ch-ua': '"Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99"',
		'sec-ch-ua-mobile': '?0',
		'sec-ch-ua-platform': '"Windows"',
		'upgrade-insecure-requests': '1',
		'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36',
		'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
		'sec-fetch-site': 'none',
		'sec-fetch-mode': 'navigate',
		'sec-fetch-user': '?1',
		'sec-fetch-dest': 'document',
		'accept-language': 'en-US,en;q=0.9',
	}

	def start_requests(self):
		yield scrapy.Request('https://bluntandcherry.ca/', headers=self.headers)

	def parse(self, response):
		img = response.xpath('//img[@title="Logo_blk"]/@src').get()
		json_body = response.xpath('//div[@class="et_pb_text_inner"]/@data-et-multi-view').get()
		contacts = eval(json_body)["schema"]["content"]["phone"].rstrip().split('\n')
		contacts = [contact.split('>', 1)[1].split('<', 1)[0] for contact in contacts]
		addr = contacts[0]
		city, province = contacts[1].split(', ')
		phone = contacts[2].replace('-', ' ')
		email = contacts[3]
		social = '|'.join(response.xpath('//ul[@class="et_pb_module et_pb_social_media_follow et_pb_social_media_follow_0_tb_footer clearfix et_pb_text_align_center et_pb_bg_layout_light"]/li/a/@href').getall())
		yield {
			"Producer ID": '',
			"p_id": self.p_id,
			"Producer": f"{self.shop_name} - {city}",
			"Description": '',
			"Link": 'https://bluntandcherry.ca/',
			"SKU": "",
			"City": city,
			"Province": province,
			"Store Name": self.shop_name,
			"Postal Code": '',
			"long": '',
			"lat": '',
			"ccc": "",
			"Page Url": 'https://bluntandcherry.ca/',
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
		yield scrapy.Request('https://bluntandcherry.ca/category/accessories/', headers=self.headers, callback=self.parse_menu)
		yield scrapy.Request('https://bluntandcherry.ca/category/cannabis/', headers=self.headers, callback=self.parse_menu)

	def parse_menu(self, response):
		products = response.xpath('//ul[@class="products columns-5"]/li/a[1]/@href').getall()
		for product in products:
			yield scrapy.Request(product, headers=self.headers, callback=self.parse_product)
		next_page = response.xpath('//a[@class="next page-numbers"]/@href').get()
		if products and next_page:
			yield scrapy.Request(f'https://bluntandcherry.ca{next_page}', callback=self.parse_menu)

	def parse_product(self, response):
		print(response.url)
		simple_product = response.xpath('(//script[@type="application/ld+json"])[3]/text()').get()
		simple_product = eval(simple_product)['@graph'][0]
		product_id = response.xpath('//link[@rel="shortlink"]/@href').get().split('=')[1]
		imgs = ['', '', '', '', '']
		images = response.xpath('//div[@class="bc-horizontal-slider-nav"]/div/img/@src').getall()
		if not images:
			img = response.xpath('//div[@class="woocommerce-product-gallery__image single-product-main-image"]/a/@href').get()
			images = [img]
		for i in range(min(len(images), 5)):
			imgs[i] = images[i]
		price = simple_product['offers'][0]['price']
		brand = response.xpath('//tr[@class="woocommerce-product-attributes-item woocommerce-product-attributes-item--attribute_pa_brand"]/td/p/text()').get()
		thc_name = ''
		cbd_name = ''
		thc = response.xpath('//tr[@class="woocommerce-product-attributes-item woocommerce-product-attributes-item--attribute_pa_thc"]/td/p/text()').get()
		cbd = response.xpath('//tr[@class="woocommerce-product-attributes-item woocommerce-product-attributes-item--attribute_pa_cbd"]/td/p/text()').get()
		cat = response.xpath('//tr[@class="woocommerce-product-attributes-item woocommerce-product-attributes-item--attribute_pa_plant-type"]/td/p/text()').get()
		weight = response.xpath('//tr[@class="woocommerce-product-attributes-item woocommerce-product-attributes-item--attribute_pa_siza"]/td/p/text()').get()
		if thc:
			thc_name = 'THC'
		if cbd:
			cbd_name = 'CBD'
		sku = simple_product['sku']
		yield {
			"Page URL": response.url,
			"Brand": brand,
			"Name": simple_product['name'],
			"SKU": sku,
			"Out stock status": "In Stock",
			"Stock count": "",
			"Currency": "CAD",
			"ccc": "",
			"Price": price,
			"Manufacturer": self.shop_name,
			"Main image": imgs[0],
			"Description": simple_product['description'],
			"Product ID": product_id,
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
			"Cat tree 1 parent": cat,
			"Cat tree 1 level 1": '',
			"Cat tree 1 level 2": "",
			"Cat tree 2 parent": "",
			"Cat tree 2 level 1": "",
			"Cat tree 2 level 2": "",
			"Cat tree 2 level 3": "",
			"Image 2": imgs[1],
			"Image 3": imgs[2],
			"Image 4": imgs[3],
			"Image 5": imgs[4],
			"Sort order": "",
			"Attribute 1": thc_name,
			"Attribute Value 1": thc,
			"Attribute 2": cbd_name,
			"Attribute value 2": cbd,
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
