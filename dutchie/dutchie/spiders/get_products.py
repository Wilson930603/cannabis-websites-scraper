import copy
import csv
import json
import os
from distutils.util import strtobool
import requests
from dutchie.items import DutchieProductItem
import scrapy
import datetime

from dutchie.spiders import api_parameters


class GetProductsSpider(scrapy.Spider):
    name = 'get_products'
    allowed_domains = []
    search_products_headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:94.0) Gecko/20100101 Firefox/94.0",
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.5",
        "accept-encoding": "gzip, deflate, br",
        "content-type": "application/json",
        "apollographql-client-name": "Marketplace (production)",
        "url": "https://dutchie.com/dispensary/spiritleaf-centre-st/products/flower",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "te": "trailers"
    }
    search_details_headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:94.0) Gecko/20100101 Firefox/94.0",
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.5",
        "accept-encoding": "gzip, deflate, br",
        "content-type": "application/json",
        "apollographql-client-name": "Marketplace (production)",
        "url": "https://dutchie.com/dispensary/spiritleaf-centre-st/product/black-cherry-punch-1g",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "te": "trailers"
    }
    search_products_url = 'https://dutchie.com/graphql?operationName=FilteredProducts&variables={{"productsFilter":{{"dispensaryId":"{0}","bypassOnlineThresholds":false}},"page":0,"perPage":5000}}&extensions={{"persistedQuery":{{"version":1,"sha256Hash":"{1}"}}}}'
    search_details_url = 'https://dutchie.com/graphql?operationName=FilteredProducts&variables={{"productsFilter":{{"productId":"{0}","bypassOnlineThresholds":false}},"hideEffects":false,"useCache":true}}&extensions={{"persistedQuery":{{"version":1,"sha256Hash":"{1}"}}}}'


    def __init__(self, city='', update_params="True", **kwargs):
        super().__init__(**kwargs)
        self.city = city.lower().replace("_", " ")
        self.update_params = bool(strtobool(update_params))

    def start_requests(self):
        if self.update_params:
            api_parameters.get_parameters(self.settings.get('PROXY_URL'))
        self.hashes = requests.get('http://3.144.196.137:1240/get').json()

        today_date = datetime.date.today().strftime("%m-%d-%y")
        full_path = f'{self.settings.get("DATA_FILE_PATH")}/{today_date}'

        file_path = f'{full_path}/Producers_{self.city} (dutchie).csv'
        if not os.path.exists(file_path):
            print(f'The Produrcer file for {self.city} does not exist. File {file_path} not found')
            return

        with open(file_path, 'r', encoding='utf-8') as f:
            header = copy.copy(self.search_products_headers)
            reader = csv.DictReader(f)
            for one in reader:
                Producer_ID = one['p_id']
                Page_Url = one['Link']
                url = self.search_products_url.format(Producer_ID, self.hashes['ProductHashWithDetails'])
                header['url'] = f"{Page_Url}/menu"
                yield scrapy.Request(
                    url=url,
                    headers=header,
                    meta={
                        'Producer_ID': Producer_ID,
                        'Page_Url': Page_Url
                    }
                )

    def parse(self, response):
        try:
            Page_Url = response.meta["Page_Url"]
            Producer_ID = response.meta["Producer_ID"]
            product_data = json.loads(response.body)
            brands = self.settings.get('BRANDS')
            if "data" in product_data:
                headers = copy.copy(self.search_details_headers)
                for product in product_data["data"]["filteredProducts"]["products"]:
                    if brands and product["brandName"] not in brands:
                        self.logger.info(f'Ignore brand: {product["brandName"]}')
                        continue
                    if product['recSpecialPrices']:
                        price = product['recSpecialPrices'][0]
                        old_price = product["Prices"][0]
                    else:
                        price = product["Prices"][0]
                        old_price = ''
                    item = DutchieProductItem()
                    item["Producer_ID"] = Producer_ID
                    item["Product_ID"] = product['id']
                    item["Page_URL"] = Page_Url + '/menu/' + product["cName"]
                    item["Brand"] = product["brandName"]
                    item["Name"] = product["Name"]
                    item["SKU"] = ''
                    item["Out_stock_status"] = product["POSMetaData"]["children"][0]["quantityAvailable"]
                    item["Currency"] = ''
                    item["ccc"] = ''
                    item["Price"] = price
                    item["Manufacturer"] = 'Dutchie'
                    item["Main_image"] = product["Image"]
                    item["Description"] = product["description"]
                    Additional_Information = json.dumps(product["effects"]) if 'effects' in product else None
                    try:
                        item["Meta_description"] = product["brand"]["description"]
                    except:
                        item["Meta_description"] = ""
                    item["Additional_Information"] = Additional_Information
                    item["Meta_title"] = ''
                    item["Old_Price"] = old_price
                    item["Equivalency_Weights"] = product["Options"][0]
                    item["Quantity"] = None
                    item["Weight"] = ''
                    item["Option"] = ''
                    item["Option_type"] = ''
                    item["Option_Value"] = ''
                    item["Option_image"] = ''
                    item["Option_price_prefix"] = ''
                    item["Cat_tree_1_parent"] = product["type"]
                    item["Cat_tree_1_level_1"] = product["subcategory"] if product["subcategory"] else ''
                    item["Cat_tree_1_level_2"] = ''
                    item["Cat_tree_2_parent"] = ''
                    item["Cat_tree_2_level_1"] = ''
                    item["Cat_tree_2_level_2"] = ''
                    item["Cat_tree_2_level_3"] = ''
                    item["Image_2"] = ''
                    item["Image_3"] = ''
                    item["Image_4"] = ''
                    item["Image_5"] = ''
                    item["Sort_order"] = ''
                    item["Attribute_1"] = 'THC'
                    item["Attribute_Value_1"] = []
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
                    yield item
        except Exception as e:
            self.logger.error(response.text)


if __name__ == '__main__':
    from scrapy.crawler import CrawlerProcess
    from scrapy.utils.project import get_project_settings

    process = CrawlerProcess(get_project_settings())
    process.crawl('get_products', city='Calgary,alberta', update_params="False")
    process.start()
