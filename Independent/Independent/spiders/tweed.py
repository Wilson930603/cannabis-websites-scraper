from Independent.spiders.base_spider import BaseSpider
import scrapy
import requests

class TweedSpider(BaseSpider):
    name = 'tweed'
    allowed_domains = ['tweed.com']
    start_urls = ['https://www.tweed.com/en/find-a-store']
    shop_name = 'Tweed'
    api_url = "https://dutchie.com/graphql"

    headers = {
        "authority": "dutchie.com",
        "apollographql-client-name": "Marketplace (production)",
        "sec-ch-ua-mobile": "?0",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
        "content-type": "application/json",
        "accept": "*/*",
        "sec-fetch-site": "same-origin",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "referer": "https://dutchie.com/",
        "accept-language": "en-US,en;q=0.9"
    }
    
    def parse(self, response):
        stores = response.xpath('//li[@class="rw-store-finder__location-list-item"]')

        stores_ids = ['tweed-kenmount-st-johns', 'tweed-corner-brook', 'tweed-regent-st', 'tweed-mount-pearl', 'tweed-water-st-st-johns', 'tweed-osborne-st-winnepeg', 'tweed-main-st-dauphin', 'tweed-victoria-ave-brandon', 'tweed-conception-bay', 'tweed-happy-valley-goose-bay', 'tweed-portage-la-parairie', 'tweed-quance', 'menu', 'menu', 'menu', 'menu', 'menu', 'menu', 'tweed-street-south-lethbridge', 'tweed-aviation-plaza', 'tweed-royal-oak', 'tweed-whyte-ave', 'tweed-ajax', 'tweed-saskatoon-8th-st-saskatchewan']
        for store in stores:
            url = store.xpath('.//a[@class="rw-store-finder__click-and-collect"]/@href').get()
            if not url:
                continue
            p_id = ''
            for item in stores_ids:
                if item in url:
                    p_id = '990099' + str(stores_ids.index(item))
                    stores_ids[stores_ids.index(item)] = 'XXXXXXXXX'
                    break
            if not p_id:
                    p_id = '0'
            yield scrapy.Request(url, callback=self.parse_store, meta={'p_id': p_id}, dont_filter=True)

    def parse_store(self, response):
        cNameOrID = response.url.split('/')[-1]
        querystring = {"operationName":"ConsumerDispensaries","variables":"{\"dispensaryFilter\":{\"cNameOrID\": \""+cNameOrID+"\"}}","extensions":"{\"persistedQuery\":{\"version\":1,\"sha256Hash\":\"26b5c68867077141fb0d4f9a341008d1d306cdb1b4bb67bf81d4bb8dfeae02d8\"}}"}
        store = requests.request("GET", self.api_url, headers=self.headers, params=querystring).json()
        description = store['data']['filteredDispensaries'][0]['description']
        yield {
            "Producer ID": '',
            "p_id": response.meta['p_id'],
            "Producer": store['data']['filteredDispensaries'][0]['name'],
            "Description": description.replace('\n', '') if description else '',
            "Link": response.url,
            "SKU": "",
            "City": store['data']['filteredDispensaries'][0]['location']['city'],
            "Province": store['data']['filteredDispensaries'][0]['location']['state'],
            "Store Name": self.shop_name,
            "Postal Code": store['data']['filteredDispensaries'][0]['address'].split(',')[-2].strip().split(' ', 1)[-1] ,
            "long": store['data']['filteredDispensaries'][0]['location']['geometry']['coordinates'][0],
            "lat": store['data']['filteredDispensaries'][0]['location']['geometry']['coordinates'][1],
            "ccc": "",
            "Page Url": response.url,
            "Active": store['data']['filteredDispensaries'][0]['status'],
            "Main image": 'https://s3-us-west-2.amazonaws.com/dutchie-images/77cdfce9af9b39bbb413a223ec51c9eb',
            "Image 2": "",
            "Image 3": "",
            "Image 4": '',
            "Image 5": '',
            "Type": "",
            "License Type": "",
            "Date Licensed": "",
            "Phone": store['data']['filteredDispensaries'][0]['phone'],
            "Phone 2": "",
            "Contact Name": "",
            "EmailPrivate": "",
            "Email": store['data']['filteredDispensaries'][0]['email'],
            "Social": "",
            "FullAddress": store['data']['filteredDispensaries'][0]['address'],
            "Address": store['data']['filteredDispensaries'][0]['address'].split(',')[0],
            "Additional Info": "",
            "Created": "",
            "Comment": "",
            "Updated": ""
        }

        dispensaryId = store['data']['filteredDispensaries'][0]['id']
        querystring = {"operationName":"DispensaryCategoriesQuery","variables":"{\"productsFilter\":{\"dispensaryId\":\""+dispensaryId+"\",\"pricingType\":\"rec\",\"Status\":\"Active\",\"removeProductsBelowOptionThresholds\":true,\"useCache\":true,\"isKioskMenu\":false}}","extensions":"{\"persistedQuery\":{\"version\":1,\"sha256Hash\":\"537c93e54dde4f87ba0623d2fde0a213a6d4690acae1b94b9e35b2b0ac775ae5\"}}"}
        categories = requests.request("GET", self.api_url, headers=self.headers, params=querystring).json()
        for category in categories['data']['filteredProducts']['categories']:
            url = response.url + '/products/' + category
            yield scrapy.Request(url, callback=self.parse_products, meta={'p_id': response.meta['p_id'], 'dispensaryId': dispensaryId, 'category': category.lower(), 'store_url': response.url}, dont_filter=True)

    def parse_products(self, response):
        p = -1
        while True:
            p += 1
            querystring = {"operationName":"FilteredProducts",
                           "variables":'{"includeCannabinoids":false,"showAllSpecialProducts":false,"productsFilter":{"dispensaryId":"'+response.meta['dispensaryId']+'","pricingType":"rec","strainTypes":[],"subcategories":[],"Status":"Active","removeProductsBelowOptionThresholds":true,"types":["'+response.meta['category'].title()+'"],"useCache":false,"sortDirection":1,"sortBy":"alpha","bypassOnlineThresholds":false,"isKioskMenu":false},"page":'+str(p)+',"perPage":50}',
                           "extensions":"{\"persistedQuery\":{\"version\":1,\"sha256Hash\":\"1d6f7daf36ba858ae6e63edf15bffd3653eaf2969167b54db1bb05faa0edb0e0\"}}"}
            
            products = requests.request("GET", self.api_url, headers=self.headers, params=querystring).json()['data']['filteredProducts']['products']

            if not products:
                break
            for product in products:
                try:
                    cName = product['cName']

                    querystring = {"operationName":"FilteredProducts","variables":"{\"includeTerpenes\":true,\"includeCannabinoids\":true,\"productsFilter\":{\"cName\":\""+product['cName']+"\",\"dispensaryId\":\""+response.meta['dispensaryId']+"\",\"removeProductsBelowOptionThresholds\":true,\"isKioskMenu\":false,\"bypassKioskThresholds\":false,\"bypassOnlineThresholds\":true}}","extensions":"{\"persistedQuery\":{\"version\":1,\"sha256Hash\":\"b0751d8ced950edb22acfee0640736693bf8879b26e95128ec6920ed1dd206f8\"}}"}
                    product = requests.request("GET", self.api_url, headers=self.headers, params=querystring).json()['data']['filteredProducts']['products'][0]

                    for option in product['Options']:
                        price = product['Prices'][product['Options'].index(option)]
                        yield {
                            "Page URL": response.meta['store_url'] + '/product/' + product['cName'],
                            "Brand": product['brandName'],
                            "Name": product['Name'],
                            "SKU": product['POSMetaData']['canonicalID'],
                            "Out stock status": 'In Stock' if product['Status'] == 'Active' else 'Out of Stock',
                            "Stock count": product['POSMetaData']['children'][0]['quantityAvailable'],
                            "Currency": "CAD",
                            "ccc": "",
                            "Price": price,
                            "Manufacturer": product['brandName'],
                            "Main image": product['Image'],
                            "Description": product['description'].replace('\n', ' ') if product['description'] else '',
                            "Product ID": product['id'],
                            "Additional Information": '',
                            "Meta description": "",
                            "Meta title": "",
                            "Old Price": product['recPrices'][0] if product['recPrices'][0] != product['Prices'][0] else '',
                            "Equivalency Weights": '',
                            "Quantity": "",
                            "Weight": '',
                            "Option": option,
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
                            "Attribute Value 1": product['THCContent']['range'][0] if product['THCContent'] and product['THCContent']['range'] else '0',
                            "Attribute 2": 'CBD',
                            "Attribute value 2": product['CBDContent']['range'][0] if product['CBDContent'] and product['CBDContent']['range'] else '0',
                            "Attribute 3": '',
                            "Attribute value 3": '',
                            "Attribute 4": '',
                            "Attribute value 4": '',
                            "Reviews": '',
                            "Review link": "",
                            "Rating": '',
                            "Address": '',
                            "p_id": response.meta['p_id']
                        }
                except:
                    pass