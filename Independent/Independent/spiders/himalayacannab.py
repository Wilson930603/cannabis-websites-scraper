from Independent.spiders.base_spider import BaseSpider
import scrapy


class HimalayaSpider(BaseSpider):
    name = 'himalayacannabis'
    allowed_domains = ['himalayacannabis.ca']
    start_urls = ['https://shop.himalayacannabis.ca/contactus']
    p_id = '990002'
    shop_name = 'Himalaya Cannabis'
    base_url = 'https://shop.himalayacannabis.ca'
    scrapped_products = []
    custom_settings = {'RETRY_TIMES': 0}

    def parse(self, response):
        details = response.xpath('//div[@class="bt_bb_column_content"]')
        details_data = details.xpath('.//div[@class="bt_bb_service_content_text"]/span/text()').getall()
        address = details_data[0]
        email = 'himalayacannabis@gmail.com'
        phone = details_data[-1]
        img = response.xpath('//a[@class="logo"]/img/@src').get()

        yield {
			"Producer ID": '',
			"p_id": self.p_id,
			"Producer": f"{self.shop_name}",
			"Description": "",
			"Link": 'https://himalayacannabis.ca',
			"SKU": "",
			"City": 'Toronto',
			"Province": 'Ontario',
			"Store Name": self.shop_name,
			"Postal Code": 'M6J 1V6',
			"long": '43.651185',
			"lat": '-79.410727',
			"ccc": "",
			"Page Url": 'https://himalayacannabis.ca/',
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

        yield scrapy.Request(self.base_url, callback=self.parse_categories, dont_filter=True)
    
    def parse_categories(self,response):
        categories = response.xpath('//div[@class="category-item"]')
        for category in categories:
            try:
                url = self.base_url + category.xpath('.//a/@href').get()
                yield scrapy.Request(url, callback=self.parse_category, dont_filter=True)
            except:
                pass
    
    def parse_category(self, response):
        categoryid = response.xpath('//div[@class="nopAjaxFilters7Spikes"]/@data-categoryid').get()
        for i in range(15):
            payload = {"categoryId": categoryid, "pageNumber": i+1, "queryString": "#/pageSize=6&viewMode=grid&orderBy=0", "shouldNotStartFromFirstPage": True}
            yield scrapy.http.JsonRequest("https://shop.himalayacannabis.ca/getFilteredProducts", data=payload, callback=self.parse_category_json, dont_filter=True)

    def parse_category_json(self, response):
        products = response.xpath('//div[@class="item-box"]')
        for product in products:
            try:
                url = self.base_url + product.xpath('.//a/@href').get()
                yield scrapy.Request(url, meta={'url': url}, callback=self.parse_product, dont_filter=True)

            except:
                pass
    
    def parse_product(self, response):
        if not response.meta['url'] in self.scrapped_products:
            self.scrapped_products.append(response.meta['url'])
        else:
            return
        name = response.xpath('//div[@class="product-name"]/h1/text()').get().replace('¼', '.25').replace('¬º', '.25')
        skuNweight = response.xpath('//div[@class="sku"]/span/text()').getall()[1].split('_')
        sku = skuNweight[0] if len(skuNweight) > 0 else ''
        weight = ''
        if len(skuNweight) > 1:
            if 'g' in skuNweight[1].lower():
                weight = skuNweight[1]

        prices = response.xpath('//div[@class="prices"]//text()').getall()
        while ' ' in prices:
            prices.remove(' ')
        if 'Your price:' in prices:
            price = prices[prices.index('Your price:')+1]
            oldPrice = prices[prices.index('Price:')+1]
        elif 'Old price:' in prices:
            price = prices[prices.index('Price:')+1]
            oldPrice = prices[prices.index('Old price:')+1]
        else:
            price = prices[0]
            oldPrice = ''

        price = price.replace('$', '').strip()
        oldPrice = oldPrice.replace('$', '').strip()

        stock = response.xpath('//div[@class="availability"]/div/span[@class="value"]/text()').get()
        if stock == '':
            stock = 'In stock'
        img_url = response.xpath('//img[@id="cloudZoomImage"]/@src').get()
        description = response.xpath('//div[@class="short-description"]/text()').get()
        if description and '•' in description and len(description) < 10:
            description = ''
        productID = response.xpath('//button[contains(@class, "add-to-wishlist-button")]/@data-productid').get()
        try:
            vendor = response.xpath('//div[@class="product-vendor"]//text()').getall()[-1]
        except:
            vendor = ''
        category = response.xpath('//span[@itemprop="name"]/text()').get()
        data_table = response.xpath('//table[@class="data-table"]')
        data = data_table.xpath('.//tr')
        atr1 = data[0].xpath('.//td[@class="spec-name"]/text()').get() if len(data) > 0 else ''
        atr1x = data[0].xpath('.//td[@class="spec-value"]/text()').get() if len(data) > 0 else ''
        atr2 = data[1].xpath('.//td[@class="spec-name"]/text()').get() if len(data) > 1 else ''
        atr2x = data[1].xpath('.//td[@class="spec-value"]/text()').get() if len(data) > 1 else ''
        atr3 = data[2].xpath('.//td[@class="spec-name"]/text()').get() if len(data) > 2 else ''
        atr3x = data[2].xpath('.//td[@class="spec-value"]/text()').get() if len(data) > 2 else ''
        atr4 = data[3].xpath('.//td[@class="spec-name"]/text()').get() if len(data) > 3 else ''
        atr4x = data[3].xpath('.//td[@class="spec-value"]/text()').get() if len(data) > 3 else ''
        product = {
				"Page URL": response.meta['url'],
				"Brand": '',
				"Name": name,
				"SKU": sku,
				"Out stock status": stock,
				"Stock count": '',
				"Currency": "CAD",
				"ccc": "",
				"Price": price,
				"Manufacturer": vendor,
				"Main image": img_url,
				"Description": description,
				"Product ID": productID,
				"Additional Information": '',
				"Meta description": "",
				"Meta title": "",
				"Old Price": oldPrice,
				"Equivalency Weights": '',
				"Quantity": "",
				"Weight": weight,
				"Option": "",
				"Option type": '',
				"Option Value": "",
				"Option image": "",
				"Option price prefix": "",
				"Cat tree 1 parent": category,
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
				"Attribute 1": atr1,
				"Attribute Value 1": atr1x,
				"Attribute 2": atr2,
				"Attribute value 2": atr2x,
				"Attribute 3": atr3,
				"Attribute value 3": atr3x,
				"Attribute 4": atr4,
				"Attribute value 4": atr4x,
				"Reviews": '',
				"Review link": "",
				"Rating": '',
				"Address": '',
				"p_id": self.p_id
			}
        for item in product:
            try:
                product[item] = product[item].replace('\n', ' ').replace('\r', '').strip()
            except:
                pass
        yield product