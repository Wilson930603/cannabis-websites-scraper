import json
from urllib.parse import urljoin

import scrapy


class A420pmSpider(scrapy.Spider):
    name = 'a420pm'
    allowed_domains = ['420pm.ca', 'dutchie.com']
    start_urls = ['https://www.420pm.ca/']
    custom_settings = {'ITEM_PIPELINES': {'dutchie.pipelines.AllInOneCSVPipeline': 300}}
    headers = {'Accept': '*/*',
               'Alt-Used': 'v3.dutchie.com',
               'apollographql-client-name': 'Marketplace (production)',
               'content-type': 'application/json'}
    products_url = 'https://v3.dutchie.com/graphql?operationName=FilteredProducts&variables=' \
                   '{{"productsFilter":{{"dispensaryId":"{p_id}",' \
                   '"pricingType":"rec","strainTypes":[],"subcategories":[],"Status":"Active",' \
                   '"removeProductsBelowOptionThresholds":true,"types":[],"useCache":false,' \
                   '"sortDirection":1,"sortBy":null,"bypassOnlineThresholds":false,"isKioskMenu":false}},' \
                   '"page":{page},"perPage":50}}&extensions={{"persistedQuery":{{"version":1,' \
                   '"sha256Hash":"dbf56616453d3565d9b1ae1cd11b5ca42c2299f7979f4ce985d6305b713a6e18"}}}}'
    details_url = 'https://v3.dutchie.com/graphql?operationName=FilteredProducts&variables=' \
                  '{{"productsFilter":{{"cName":"{product_cname}","dispensaryId":"{p_id}",' \
                  '"removeProductsBelowOptionThresholds":true,"isKioskMenu":false,"bypassKioskThresholds":false,' \
                  '"bypassOnlineThresholds":true}}}}&extensions={{"persistedQuery":{{"version":1,' \
                  '"sha256Hash":"985da6bc0d8fddb0f8f9b0d2940c2f09729534396da528fc74c7105615597031"}}}}'

    def parse(self, response, **kwargs):
        links = response.xpath('//nav[@class="header-nav-list"]'
                               '/div[@class="header-nav-item header-nav-item--folder"]'
                               '/div[@class="header-nav-folder-content"]'
                               '/div[@class="header-nav-folder-item"]/a/@href').extract()
        for link in links:
            url = urljoin(self.start_urls[0], link)
            yield scrapy.Request(url,
                                 callback=self.parse_shop_home)

    def parse_shop_home(self, response):
        dutchie_script = response.xpath('//script[@id="dutchie--embed__script"]/@src').extract_first()
        if not dutchie_script:
            return
        yield scrapy.Request(dutchie_script,
                             callback=self.parse_dutchie_script)

    def parse_dutchie_script(self, response):
        indicator = '__DTCHE.DutchieEmbedder(w, '
        index1 = response.text.find(indicator)
        if index1 < 0:
            return
        index1 += len(indicator)
        index2 = response.text.find(');', index1)
        dutchie_embedder = response.text[index1: index2]
        dutchie_embedder = json.loads(dutchie_embedder)
        store_cname = dutchie_embedder['cName']

        store_url = f'https://v3.dutchie.com/graphql?operationName=ConsumerDispensaries&variables=' \
                    f'{{"dispensaryFilter":{{"cNameOrID":"{store_cname}"}}}}' \
                    f'&extensions={{"persistedQuery":{{"version":1,' \
                    f'"sha256Hash":"16d5bb2518b793881d77a42d394400b123f91f93dced24fbd2c621ebe8db3a6f"}}}}'
        yield scrapy.Request(store_url,
                             headers=self.headers,
                             callback=self.parse_store,
                             meta={'store_cname': store_cname})

    def parse_store(self, response):
        result = json.loads(response.text)
        stores = result['data']['filteredDispensaries']
        for store in stores:
            p_id = store['id']
            location = store.get('location')
            item = {"Producer ID": "",
                    "p_id": p_id,
                    "Producer": f'{store["name"]} - {location.get("city")}',
                    "Description": store.get('description'),
                    "Link": f'https://dutchie.com/dispensaries/{store["cName"]}',
                    "SKU": "",
                    "City": location.get('city'),
                    "Province": location.get('state'),
                    "Store Name": store.get('name'),
                    "Postal Code": '',
                    "long": '',
                    "lat": '',
                    "ccc": "",
                    "Page Url": '',
                    "Active": "",
                    "Main image": store.get('listImage'),
                    "Image 2": '',
                    "Image 3": '',
                    "Image 4": '',
                    "Image 5": '',
                    "Type": store["__typename"] if store["__typename"] else 'Unknown',
                    "License Type": "",
                    "Date Licensed": "",
                    "Phone": store.get('phone'),
                    "Phone 2": "",
                    "Contact Name": "",
                    "EmailPrivate": "",
                    "Email": store.get('email'),
                    "Social": "",
                    "FullAddress": store.get('address'),
                    "Address": store.get('address'),
                    "Additional Info": "",
                    "Created": '',
                    "Comment": "",
                    "Updated": ''}
            if 'geometry' in location and location['geometry']:
                if 'coordinates' in location['geometry'] and location['geometry']['coordinates']:
                    item['long'] = location['geometry']['coordinates'][0]
                    item['lat'] = location['geometry']['coordinates'][1]
            yield item

            query_url = self.products_url.format(p_id=p_id, page=0)
            yield scrapy.Request(query_url,
                                 headers=self.headers,
                                 callback=self.parse_products,
                                 meta={'p_id': p_id,
                                       'page': 0,
                                       'store_cname': response.meta['store_cname']})

    def parse_products(self, response):
        p_id = response.meta['p_id']
        store_cname = response.meta['store_cname']
        brands = self.settings.get('BRANDS')

        result = json.loads(response.text)
        products = result['data']['filteredProducts']['products']
        for product in products:
            if brands and product["brandName"] not in brands:
                self.logger.info(f'Ignore brand: {product["brandName"]}')
                continue

            if product['recSpecialPrices']:
                price = product['recSpecialPrices'][0]
                old_price = product["Prices"][0]
            else:
                price = product["Prices"][0]
                old_price = ''

            item = {"Product_ID": product['id'],
                    "Page URL": f'https://v3.dutchie.com/embedded-menu/{store_cname}/product/{product["cName"]}',
                    "Brand": product["brandName"],
                    "Name": product["Name"],
                    "SKU": '',
                    "Out_stock_status": product["POSMetaData"]["children"][0]["quantityAvailable"],
                    "Currency": '',
                    "ccc": '',
                    "Price": price,
                    "Manufacturer": 'Dutchie',
                    "Main_image": product["Image"],
                    "Description": '',
                    "Additional_Information": '',
                    "Meta_description": '',
                    "Meta_title": '',
                    "Old_Price": old_price,
                    "Equivalency_Weights": product["Options"][0],
                    "Quantity": None,
                    "Weight": '',
                    "Option": '',
                    "Option_type": '',
                    "Option_Value": '',
                    "Option_image": '',
                    "Option_price_prefix": '',
                    "Cat_tree_1_parent": product["type"],
                    "Cat_tree_1_level_1": product["subcategory"] if product["subcategory"] else '',
                    "Cat_tree_1_level_2": '',
                    "Cat_tree_2_parent": '',
                    "Cat_tree_2_level_1": '',
                    "Cat_tree_2_level_2": '',
                    "Cat_tree_2_level_3": '',
                    "Image_2": '',
                    "Image_3": '',
                    "Image_4": '',
                    "Image_5": '',
                    "Sort_order": '',
                    "Attribute_1": 'THC',
                    "Attribute_Value_1": []}
            if product["THCContent"]:
                if product["THCContent"]["range"]:
                    for THC in product["THCContent"]["range"]:
                        if THC:
                            item["Attribute_Value_1"].append(str(THC))
            item["Attribute_Value_1"] = ' - '.join(item["Attribute_Value_1"])
            item["Attribute_2"] = 'CBD'
            item["Attribute_value_2"] = []
            if product["CBDContent"]:
                if product["CBDContent"]["range"]:
                    for CBD in product["CBDContent"]["range"]:
                        if CBD:
                            item["Attribute_value_2"].append(str(CBD))
            item["Attribute_value_2"] = ' - '.join(item["Attribute_value_2"])
            item["Attribute_3"] = 'Type'
            item["Attribute_value_3"] = product["type"]
            item["Attribute_4"] = ''
            item["Attribute_value_4"] = ''
            item["Reviews"] = ''
            item["Review_link"] = ''
            item["Rating"] = ''
            item['p_id'] = p_id
            details_url = self.details_url.format(product_cname=product['cName'], p_id=p_id)
            yield scrapy.Request(details_url,
                                 headers=self.headers,
                                 callback=self.parse_product_details,
                                 meta={'item': item})

        query_info = result['data']['filteredProducts']['queryInfo']
        if response.meta['page'] == 0:
            for page in range(1, query_info['totalPages']):
                query_url = self.products_url.format(p_id=p_id, page=page)
                yield scrapy.Request(query_url,
                                     headers=self.headers,
                                     callback=self.parse_products,
                                     meta={'p_id': p_id,
                                           'page': page,
                                           'store_cname': store_cname})

    def parse_product_details(self, response):
        item = response.meta["item"]
        result = json.loads(response.text)
        product = result["data"]["filteredProducts"]["products"][0]
        item["Description"] = product.get('description')

        additional_information = json.dumps(product["effects"]) if 'effects' in product else None
        item["Additional_Information"] = additional_information

        brand_data = product.get('brand')
        if brand_data:
            item["Meta_description"] = brand_data.get('description')

        options = product.get('Options')
        if options:
            for index, sku in enumerate(options):
                item['SKU'] = sku
                item['Option_type'] = 'Select'
                item['Option_Value'] = sku
                if product['recSpecialPrices']:
                    item['Price'] = item['Option_price_prefix'] = product['recSpecialPrices'][index]
                else:
                    item['Price'] = item['Option_price_prefix'] = product['recPrices'][index]
                item['Old_Price'] = product['recPrices'][index]
                yield item
        else:
            yield item


if __name__ == '__main__':
    from scrapy.crawler import CrawlerProcess
    from scrapy.utils.project import get_project_settings

    process = CrawlerProcess(get_project_settings())
    process.crawl('a420pm', update_params="True")
    process.start()
