from Independent.spiders.base_spider import BaseSpider
import scrapy
import requests
import json


class MaryJSpider(BaseSpider):
    name = 'maryjcannabis'
    allowed_domains = ['maryjcannabis.ca']
    stores = {
        '3216': 'https://shop.maryjcannabis.ca/embed/stores/3216/menu',
        '3217': 'https://menu.maryjcannabis.ca/embed/stores/3217/menu'
    }
    start_urls = ['https://menu.maryjcannabis.ca/embed/stores']

    def parse(self, response):
        api_url = "https://menu.maryjcannabis.ca/api/v1/stores/"
        for p_id in self.stores:
            yield scrapy.Request(api_url + p_id, meta={'p_id': p_id}, callback=self.parse_store, dont_filter=True) 
    
    def parse_store(self, response):
        jsonresponse = json.loads(response.text)
        
        yield {
			"Producer ID": '',
			"p_id": response.meta['p_id'],
			"Producer": jsonresponse['store']['name'],
			"Description": jsonresponse['store']['description'],
			"Link": 'https://shop.maryjcannabis.ca',
			"SKU": "",
			"City": jsonresponse['store']['city'],
			"Province": jsonresponse['store']['state'],
			"Store Name": jsonresponse['store']['name'],
			"Postal Code": jsonresponse['store']['zip'],
			"long": jsonresponse['store']['long'],
			"lat": jsonresponse['store']['lat'],
			"ccc": "",
			"Page Url": 'https://shop.maryjcannabis.ca/',
			"Active": "",
			"Main image": jsonresponse['store']['photo'],
			"Image 2": "",
			"Image 3": "",
			"Image 4": '',
			"Image 5": '',
			"Type": "",
			"License Type": "",
			"Date Licensed": "",
			"Phone": jsonresponse['store']['phone'],
			"Phone 2": "",
			"Contact Name": "",
			"EmailPrivate": "",
			"Email": '',
			"Social": "",
			"FullAddress": jsonresponse['store']['full_address'],
			"Address": jsonresponse['store']['address'],
			"Additional Info": "",
			"Created": "",
			"Comment": "",
			"Updated": ""
        }

        url ='https://vfm4x0n23a-3.algolianet.com/1/indexes/*/queries'
        params = {
        'x-algolia-agent': 'Algolia for JavaScript (4.5.1); Browser (lite); JS Helper (3.1.1); react (16.13.1); react-instantsearch (6.4.0)',
        'x-algolia-application-id': 'VFM4X0N23A',
        'x-algolia-api-key': 'b499e29eb7542dc373ec0254e007205d'}
        data = {"requests":[{"indexName":"menu-products-production","params":f'query=&hitsPerPage=1000&filters=store_id = {response.meta["p_id"]}'}]}
        jsonObj = requests.post(url, data=json.dumps(data), params=params).json()
        for product in jsonObj['results'][0]['hits']:
            img1 = product['image_urls'][0] if len(product['image_urls']) >= 1 else ''
            img2 = product['image_urls'][1] if len(product['image_urls']) > 1 else ''
            img3 = product['image_urls'][2] if len(product['image_urls']) > 2 else ''
            img4 = product['image_urls'][3] if len(product['image_urls']) > 3 else ''
            img5 = product['image_urls'][4] if len(product['image_urls']) > 4 else ''
            attributes = product['description'].split('\n')
            thc = attributes[0].replace('THC:', '').strip() if 'THC:' in attributes[0] else ''
            cbd = attributes[1].replace('CBD:', '').strip() if len(attributes) > 1 and 'CBD:' in attributes[1] else ''
            # price = product['sort_price'] if not product['price_eighth_ounce'] else product['discounted_price_eighth_ounce'] if product['discounted_price_eighth_ounce'] else product['price_eighth_ounce']
            # old_price = ''
            # try:
            #     old_price = product['price_each'] if int(product['price_each']) != int(price) else ''
            # except:
            #     pass
            price = product['sort_price']
            old_price = product['sort_price']

            if product['price_half_gram']:
                price = product['discounted_price_half_gram']  if product['discounted_price_half_gram'] else product['price_half_gram']
                old_price = product['price_half_gram'] if price != product['price_half_gram'] else ''
            elif product['price_ounce']:
                price = product['discounted_price_ounce']  if product['discounted_price_ounce'] else product['price_ounce']
                old_price = product['price_ounce'] if price != product['price_ounce'] else ''
            elif product['price_half_ounce']:
                price = product['discounted_price_half_ounce']  if product['discounted_price_half_ounce'] else product['price_half_ounce']
                old_price = product['price_half_ounce'] if price != product['price_half_ounce'] else ''
            elif product['price_quarter_ounce']:
                price = product['discounted_price_quarter_ounce']  if product['discounted_price_quarter_ounce'] else product['price_quarter_ounce']
                old_price = product['price_quarter_ounce'] if price != product['price_quarter_ounce'] else ''
            elif product['price_eighth_ounce']:
                price = product['discounted_price_eighth_ounce'] if product['discounted_price_eighth_ounce'] else product['price_eighth_ounce']
                old_price = product['price_eighth_ounce'] if price != product['price_eighth_ounce'] else ''
            elif product['price_two_gram']:
                price = product['discounted_price_two_gram']  if product['discounted_price_two_gram'] else product['price_two_gram']
                old_price = product['price_two_gram'] if price != product['price_two_gram'] else ''
            
            if old_price == price:
                old_price = ''


            yield {
                "Page URL": f'https://shop.maryjcannabis.ca/embed/stores/{response.meta["p_id"]}/products/{product["product_id"]}/{product["url_slug"]}',
                "Brand": product['brand'],
                "Name": product['name'],
                "SKU": '',
                "Out stock status": 'In Stock' if int(product['max_cart_quantity']) > 0 else 'Out of Stock',
                "Stock count": product['max_cart_quantity'],
                "Currency": "CAD",
                "ccc": "",
                "Price": price,
                "Manufacturer": jsonresponse['store']['name'],
                "Main image": img1,
                "Description": product['store_notes'].replace('\n', ' ') if product['store_notes'] != None else '',
                "Product ID": product['product_id'],
                "Additional Information": '',
                "Meta description": "",
                "Meta title": "",
                "Old Price": old_price,
                "Equivalency Weights": '',
                "Quantity": "",
                "Weight": product['amount'],
                "Option": "",
                "Option type": '',
                "Option Value": "",
                "Option image": "",
                "Option price prefix": "",
                "Cat tree 1 parent": product['category'],
                "Cat tree 1 level 1": product['root_subtype'],
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
                "Attribute 1": 'THC' if thc else '',
                "Attribute Value 1": thc,
                "Attribute 2": 'CBD' if cbd else '',
                "Attribute value 2": cbd,
                "Attribute 3": '',
                "Attribute value 3": '',
                "Attribute 4": '',
                "Attribute value 4": '',
                "Reviews": product['review_count'] if product['review_count'] != '0' else '',
                "Review link": "",
                "Rating": product['aggregate_rating'] if product['aggregate_rating'] != '0.0' else '',
                "Address": '',
                "p_id": response.meta["p_id"]
            }