from Independent.spiders.base_spider import BaseSpider
import scrapy
import json


class LovebudSpider(BaseSpider):
    name = 'lovebud'
    allowed_domains = ['lovebud.shop']
    start_urls = ['https://lovebud.shop/api/shop/customdomain/lovebud.shop']
    p_id = '990026'

    def parse(self, response):
        jsonresponse = json.loads(response.text)
        shop_name = jsonresponse['shop']['name']
        img = jsonresponse['shop']['logoSrc']
        createdAt = jsonresponse['shop']['createdAt'].replace('T', ' | ')
        updatedAt = jsonresponse['shop']['updatedAt'].replace('T', ' | ')
        description = jsonresponse['shop']['description']
        address = jsonresponse['shop']['locations'][0]['address']
        city = jsonresponse['shop']['locations'][0]['city']
        postal_code = jsonresponse['shop']['locations'][0]['postalCode']
        

        yield {
			"Producer ID": '',
			"p_id": self.p_id,
			"Producer": f"{shop_name}",
			"Description": description,
			"Link": 'https://lovebud.shop',
			"SKU": "",
			"City": city,
			"Province": 'Ontario',
			"Store Name": shop_name,
			"Postal Code": postal_code,
			"long": '',
			"lat": '',
			"ccc": "",
			"Page Url": 'https://lovebud.shop',
			"Active": "",
			"Main image": img,
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
			"Email": '',
			"Social": "",
			"FullAddress": address,
			"Address": '',
			"Additional Info": "",
			"Created": createdAt,
			"Comment": '',
			"Updated": updatedAt
        }

        for product in jsonresponse['shop']['products']:
            img2 = product['media'][1]['src'] if len(product['media']) > 2 else ''
            img3 = product['media'][2]['src'] if len(product['media']) > 3 else ''
            img4 = product['media'][3]['src'] if len(product['media']) > 4 else ''
            img5 = product['media'][4]['src'] if len(product['media']) > 5 else ''

            yield {
                "Page URL": 'https://lovebud.shop/product/' + str(product['variants'][0]['productId']),
                "Brand": product['vendor'],
                "Name": product['title'],
                "SKU": product['variants'][0]['sku'].split('_')[0] if product['variants'][0]['sku'] else '',
                "Out stock status": 'In Stock' if product['variants'][0]['inventoryQuantity'] != '0' else 'Out of Stock',
                "Stock count": product['variants'][0]['inventoryQuantity'],
                "Currency": "CAD",
                "ccc": "",
                "Price": product['variants'][0]['price'],
                "Manufacturer": product['vendor'],
                "Main image": product['coverPhotoSrc'],
                "Description": product['description'].replace('\n', ' '),
                "Product ID": product['variants'][0]['productId'],
                "Additional Information": '',
                "Meta description": "",
                "Meta title": "",
                "Old Price": '',
                "Equivalency Weights": '',
                "Quantity": '',
                "Weight": product['variants'][0]['sku'].split('_')[1] if product['variants'][0]['sku'] and len(product['variants'][0]['sku'].split('_')) > 1 else '',
                "Option": "",
                "Option type": '',
                "Option Value": "",
                "Option image": "",
                "Option price prefix": "",
                "Cat tree 1 parent": product['category'],
                "Cat tree 1 level 1": "",
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
                "Attribute 1": product['highlights'][0]['title'] if len(product['highlights']) > 0 else '',
                "Attribute Value 1": product['highlights'][0]['body'] if len(product['highlights']) > 0 else '',
                "Attribute 2": product['highlights'][1]['title'] if len(product['highlights']) > 1 else '',
                "Attribute value 2": product['highlights'][1]['body'] if len(product['highlights']) > 1 else '',
                "Attribute 3": product['highlights'][2]['title'] if len(product['highlights']) > 2 else '',
                "Attribute value 3": product['highlights'][2]['body'] if len(product['highlights']) > 2 else '',
                "Attribute 4": product['highlights'][3]['title'] if len(product['highlights']) > 3 else '',
                "Attribute value 4": product['highlights'][3]['body'] if len(product['highlights']) > 3 else '',
                "Reviews": '',
                "Review link": '',
                "Rating": '',
                "Address": '',
                "p_id": self.p_id
            }