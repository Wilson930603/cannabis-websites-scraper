from Independent.spiders.base_spider import BaseSpider
import scrapy
import requests


class MaryJSpider(BaseSpider):
    name = 'northernhigh'
    p_id = '990043'
    shop_name = 'Northern High'
    
    def start_requests(self):
        url = 'https://northern-high.ca/contact-us/'
        yield scrapy.Request(url=url, callback=self.parse, meta={'proxy': ''})

    
    def parse(self, response):
        full_address = ''.join(response.xpath('//div[@class="et_pb_text_inner"]/p/text()').getall()).replace('\n', '')
        email = response.xpath('//div[@class="et_pb_text_inner"]/p[2]/a[1]/text()')[-1].get().replace('Email: ', '')
        phone = response.xpath('//div[@class="et_pb_text_inner"]/p[2]/a[2]/text()')[-1].get().replace('Phone:', '')
        yield {
			"Producer ID": '',
			"p_id": self.p_id,
			"Producer": self.shop_name,
			"Description": '',
			"Link": 'https://northern-high.ca',
			"SKU": "",
			"City": 'Minden',
			"Province": full_address.split(',')[1],
			"Store Name": self.shop_name,
			"Postal Code": full_address.split(',')[2],
			"long": '44.924763',
			"lat": '-78.723829',
			"ccc": "",
			"Page Url": 'https://northern-high.ca/',
			"Active": "Yes",
			"Main image": response.xpath('//img[@id="logo"]/@src').get(),
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
			"FullAddress": full_address,
			"Address": full_address.split(',')[0],
			"Additional Info": "",
			"Created": "",
			"Comment": "",
			"Updated": ""
        }

        url = "https://northernhighwebmenu-api.azurewebsites.net/api/products/filterProducts"
        payload = {"ProductGroupId":"","SortId":1,"Page":1,"PageSize":2000,"SearchText":"","Brand":"","Weight":"","Species":"","BranchId":1,"Terpene":"","THCMAX":100,"THCMIN":0,"CBDMAX":100,"CBDMIN":0}
        jsonObj = requests.request("POST", url, json=payload).json()
        for product in jsonObj['data']['products']:
            yield {
                "Page URL": 'https://northernhighwebmenu.azurewebsites.net/product/' + str(product['id']),
                "Brand": product['brand'],
                "Name": product['name'],
                "SKU": product['sku'].split('_')[0].replace('"', ''),
                "Out stock status": 'In Stock' if product['quantity'] else 'Out of Stock',
                "Stock count": product['quantity'],
                "Currency": "CAD",
                "ccc": "",
                "Price": product['price']['discountedPrice'],
                "Manufacturer": product['brand'],
                "Main image": product['imagesUrls'][0] if product['imagesUrls'] else '',
                "Description": product['description'].replace('\n', '') if product['description'] else '',
                "Product ID": product['id'],
                "Additional Information": '',
                "Meta description": "",
                "Meta title": "",
                "Old Price": product['price']['price'] if product['price']['discountedPrice'] != product['price']['price'] else '',
                "Equivalency Weights": '',
                "Quantity": "",
                "Weight": product['sku'].split('_')[1] if len(product['sku'].split('_')) > 1 and 'AMZN' not in product['sku'].split('_')[1] else '',
                "Option": "",
                "Option type": '',
                "Option Value": "",
                "Option image": "",
                "Option price prefix": "",
                "Cat tree 1 parent": product['category'],
                "Cat tree 1 level 1": '',
                "Cat tree 1 level 2": "",
                "Cat tree 2 parent": '',
                "Cat tree 2 level 1": "",
                "Cat tree 2 level 2": "",
                "Cat tree 2 level 3": "",
                "Image 2": product['imagesUrls'][1] if product['imagesUrls'] and len(product['imagesUrls']) > 1 else '',
                "Image 3": product['imagesUrls'][2] if product['imagesUrls'] and len(product['imagesUrls']) > 2 else '',
                "Image 4": product['imagesUrls'][3] if product['imagesUrls'] and len(product['imagesUrls']) > 3 else '',
                "Image 5": product['imagesUrls'][4] if product['imagesUrls'] and len(product['imagesUrls']) > 4 else '',
                "Sort order": "THC" if product['thC_LEVEL'] else '',
                "Attribute 1": product['thC_LEVEL'] if product['thC_LEVEL'] else '',
                "Attribute Value 1": '',
                "Attribute 2": 'CBD' if product['cbD_LEVEL'] else '',
                "Attribute value 2": product['cbD_LEVEL'] if product['cbD_LEVEL'] else '',
                "Attribute 3": 'Terpenes' if product['terpenes'] else '',
                "Attribute value 3": ', '.join(product['terpenes']),
                "Attribute 4": '',
                "Attribute value 4": '',
                "Reviews": '',
                "Review link": "",
                "Rating": '',
                "Address": '',
                "p_id": self.p_id
            }