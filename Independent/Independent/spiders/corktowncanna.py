from Independent.spiders.base_spider import BaseSpider
import scrapy
import requests

class CorkTownSpider(BaseSpider):
    name = 'corktowncanna'
    allowed_domains = ['corktowncanna.com']
    start_urls = ['https://5buds.ca/contact/']
    shop_name = 'CorkTown Cannabis Company'
    p_id = '990112'
    
    def parse(self, response):
        yield {
            "Producer ID": '',
            "p_id": self.p_id,
            "Producer": self.shop_name,
            "Description": '',
            "Link": 'https://www.corktowncanna.com/',
            "SKU": "",
            "City": 'Russell',
            "Province": 'MB',
            "Store Name": self.shop_name,
            "Postal Code": 'R0J 1W0',
            "long": '',
            "lat": '',
            "ccc": "",
            "Page Url": 'https://www.corktowncanna.com/',
            "Active": 'Yes',
            "Main image": 'https://www.corktowncanna.com/wp-content/uploads/2020/03/final-logo.png',
            "Image 2": "",
            "Image 3": "",
            "Image 4": '',
            "Image 5": '',
            "Type": "",
            "License Type": "",
            "Date Licensed": "",
            "Phone": '1 204 773 4795',
            "Phone 2": "",
            "Contact Name": "",
            "EmailPrivate": "",
            "Email": 'info@corktown.com',
            "Social": ['https://www.instagram.com/corktowncannabis/', 'https://twitter.com/CompanyCorktown', 'https://facebook.com/CorktownCanna/'],
            "FullAddress": '117 Assiniboine St. West, Russell MB, R0J1W0',
            "Address": '117 Assiniboine St. West',
            "Additional Info": "",
            "Created": "",
            "Comment": "",
            "Updated": ""
        }
        
        yield scrapy.Request('https://www.superanytime.com', callback=self.parse_product, dont_filter=True)
        
    def parse_product(self, response):
        url = "https://www.superanytime.com/api/search"
        querystring = {"storeId":"2932d4fa-40f7-45b3-b680-50878b0aee9a","query":"","category":"","offset":"0","minPrice":"0","maxPrice":"2147483647","limit":"10000"}
        headers = {
            "authorization": "null",
            "sec-ch-ua-mobile": "?0",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
            "accept": "*/*",
            "sec-fetch-site": "same-origin",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": "https://www.superanytime.com/store-embedded/2932d4fa-40f7-45b3-b680-50878b0aee9a",
            "accept-language": "en-US,en;q=0.9"
        }

        products = requests.request("GET", url, headers=headers, params=querystring).json()['products']
        for product in products:
            disc = product['description']
            disc = disc.replace('\n', '').strip() if disc else ''
            yield {
                "Page URL": 'https://www.superanytime.com/store-embedded/2932d4fa-40f7-45b3-b680-50878b0aee9a/product/' + product['id'],
                "Brand": self.shop_name,
                "Name": product['title'],
                "SKU": '',
                "Out stock status": 'In Stock' if not product['outOfStock'] else 'Out of Stock',
                "Stock count": product['quantity'],
                "Currency": "CAD",
                "ccc": "",
                "Price": product['price'] / 100,
                "Manufacturer": self.shop_name,
                "Main image": product['imageURL'],
                "Description": disc,
                "Product ID": product['id'],
                "Additional Information": '',
                "Meta description": '',
                "Meta title":  '',
                "Old Price": '',
                "Equivalency Weights": '',
                "Quantity": '',
                "Weight": product['grams'],
                "Option": "",
                "Option type": '',
                "Option Value": "",
                "Option image": "",
                "Option price prefix": "",
                "Cat tree 1 parent": product['type'],
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
                "Sort order": '',
                "Attribute 1": 'THC',
                "Attribute Value 1": product['thc'],
                "Attribute 2": 'CBD',
                "Attribute value 2": product['cbd'],
                "Attribute 3": 'Alcohol Vol',
                "Attribute value 3": product['alcoholVol'],
                "Attribute 4": '',
                "Attribute value 4": '',
                "Reviews": '',
                "Review link": "",
                "Rating": '',
                "Address": '',
                "p_id": self.p_id
            }