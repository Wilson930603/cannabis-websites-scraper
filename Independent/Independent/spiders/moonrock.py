from Independent.spiders.base_spider import BaseSpider
import scrapy
import json

class MoonRockSpider(BaseSpider):
    name = 'moonrock'
    start_urls = ['https://moonrockcanada.com/contact/']
    p_id = '990040'
    store_name = 'Moon Rock Canada'

    def parse(self, response):
        yield {
			"Producer ID": '',
			"p_id": self.p_id,
			"Producer": self.store_name,
			"Description": '',
			"Link": 'https://moonrockcanada.com',
			"SKU": "",
			"City": '',
			"Province": '',
			"Store Name": self.store_name,
			"Postal Code": '',
			"long": '',
			"lat": '',
			"ccc": "",
			"Page Url": 'https://moonrockcanada.com/',
			"Active": "",
			"Main image": 'https://moonrockcanada.com/wp-content/uploads/2021/05/moon_rock_logo_silvery.png',
			"Image 2": "",
			"Image 3": "",
			"Image 4": '',
			"Image 5": '',
			"Type": "",
			"License Type": "",
			"Date Licensed": "",
			"Phone": '',
			"Phone 2": "",
			"Contact Name": "",
			"EmailPrivate": "",
			"Email": 'info@moonrockcanada.com',
			"Social": "https://www.facebook.com/moonrockcanada | https://www.instagram.com/moonrockcanadaofficial/",
			"FullAddress": '',
			"Address": '',
			"Additional Info": "",
			"Created": "",
			"Comment": "",
			"Updated": ""
        }

        yield scrapy.Request('https://moonrockcanada.com/shop/page/1', callback=self.parse_products, dont_filter=True)

    scraped_pages = 1
    def parse_products(self, response):
        
        products = response.xpath('//div[contains(@class, "product-small box")]')
        for product in products:
            url = product.xpath('.//a/@href').get()
            yield scrapy.Request(url, callback=self.parse_product, dont_filter=True)

        if len(products):
            self.scraped_pages += 1
            yield scrapy.Request('https://moonrockcanada.com/shop/page/' + str(self.scraped_pages), callback=self.parse_products, dont_filter=True)
    
    def parse_product(self, response):
        imgs = response.xpath('//img[@class="wp-post-image skip-lazy"]/@src')
        img = imgs[0].get() if len(imgs) > 0 else ''
        img2 = imgs[1].get() if len(imgs) > 1 else ''
        img3 = imgs[2].get() if len(imgs) > 2 else ''
        img4 = imgs[3].get() if len(imgs) > 3 else ''
        img5 = imgs[4].get() if len(imgs) > 4 else ''

        attr1_name = attr1_value = attr2_name = attr2_value = attr3_name = attr3_value = attr4_name = attr4_value = ''
        try:
            formData = json.loads(response.xpath('//form[contains(@class,"cart")]/@data-product_variations').get())
            if len(formData) > 0:
                attr1_name = list(formData[0]['attributes'])[0]
                attr1_value = next(iter(formData[0]['attributes'].values()))
            if len(formData) > 1:
                attr2_name = list(formData[1]['attributes'])[0]
                attr2_value = next(iter(formData[1]['attributes'].values()))
            if len(formData) > 2:
                attr3_name = list(formData[2]['attributes'])[0]
                attr3_value = next(iter(formData[2]['attributes'].values()))
            if len(formData) > 3:
                attr4_name = list(formData[3]['attributes'])[0]
                attr4_value = next(iter(formData[3]['attributes'].values()))
        except:
            pass

        try:
            option1 = formData[1]['attributes']['attribute_amount']
            option1_price = formData[1]['display_price']
        except:
            option1 = option1_price = ''
        reviews = response.xpath('//a[@href="#tab-reviews"]/text()').get().split('(')[-1].split(')')[0]
        try:
            max_qty = int(response.xpath('//p[contains(@class,"stock")]/text()').get().split(' ')[0])
        except:
            max_qty = ''
        sku = response.xpath('//span[@class="sku"]/text()').get()
        price = response.xpath('//div[@class="price-wrapper"]/p/span/bdi/text()').get()
        oldPrice = ''
        if not price:
            price = response.xpath('//div[@class="price-wrapper"]/p/ins/span/bdi/text()').get()
            oldPrice = response.xpath('//div[@class="price-wrapper"]/p/del/span/bdi/text()').get()
        yield {
            "Page URL": response.url,
            "Brand": '',
            "Name": response.xpath('//h1/text()').get(),
            "SKU": sku if sku != 'N/A' else '',
            "Out stock status": 'In Stock' if price else 'Out of Stock',
            "Stock count": max_qty,
            "Currency": "CAD",
            "ccc": "",
            "Price": price,
            "Manufacturer": '',
            "Main image": img,
            "Description": ' '.join(response.xpath('//div[@id="tab-description"]//text()').getall()).replace('\n', ' '),
            "Product ID": response.xpath('//form[@class="variations_form cart"]/@data-product_id').get(),
            "Additional Information": '',
            "Meta description": "",
            "Meta title": "",
            "Old Price": oldPrice,
            "Equivalency Weights": '',
            "Quantity": "",
            "Weight": '',
            "Option": option1,
            "Option type": '',
            "Option Value": '',
            "Option image": "",
            "Option price prefix": option1_price,
            "Cat tree 1 parent": response.xpath('//span[@class="posted_in"]/a/text()').get(),
            "Cat tree 1 level 1": '',
            "Cat tree 1 level 2": "",
            "Cat tree 2 parent": '',
            "Cat tree 2 level 1": "",
            "Cat tree 2 level 2": "",
            "Cat tree 2 level 3": "",
            "Image 2": img2,
            "Image 3": img3,
            "Image 4": img4,
            "Image 5": img5,
            "Sort order": "",
            "Attribute 1": attr1_name.replace('attribute_', ''),
            "Attribute Value 1": attr1_value,
            "Attribute 2": attr2_name.replace('attribute_', ''),
            "Attribute value 2": attr2_value,
            "Attribute 3": attr3_name.replace('attribute_', ''),
            "Attribute value 3": attr3_value,
            "Attribute 4": attr4_name.replace('attribute_', ''),
            "Attribute value 4": attr4_value,
            "Reviews": reviews if reviews != '0' else '',
            "Review link": response.url + '#tab-reviews' if reviews != '0' else '',
            "Rating": response.xpath('//strong[@class="rating"]/text()').get(),
            "Address": '',
            "p_id": self.p_id
        }