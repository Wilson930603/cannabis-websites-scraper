import json
import logging
import os
import time
import traceback
from typing import Optional
from urllib.parse import urlsplit, parse_qs, unquote

from selenium.webdriver import DesiredCapabilities
from tenacity import retry, stop_after_attempt, wait_exponential
import selenium
from seleniumwire import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from seleniumwire.request import HTTPHeaders


class BrowseDutchie:
    json_file_name = 'api_parameters.json'

    def __init__(self, proxy_url=None):
        self.proxy_url = proxy_url
        self.parameters = {}

        selenium.webdriver.remote.remote_connection.LOGGER.setLevel(logging.ERROR)
        logging.getLogger('seleniumwire').setLevel(logging.ERROR)
        logging.getLogger("urllib3").propagate = False
        logging.getLogger("hpack.hpack").propagate = False

    def __enter__(self):
        firefox_options = webdriver.FirefoxOptions()
        # firefox_options.headless = True
        firefox_options.set_preference("dom.webdriver.enabled", False)
        firefox_options.set_preference("useAutomationExtension", False)
        if self.proxy_url:
            sw_options = {
                'proxy': {
                    'http': self.proxy_url,
                    'https': self.proxy_url,
                    'no_proxy': 'localhost,127.0.0.1'
                }
            }
        else:
            sw_options = None
        caps = DesiredCapabilities.FIREFOX.copy()
        self.driver = webdriver.Firefox(options=firefox_options,
                                        seleniumwire_options=sw_options,
                                        service_log_path=os.devnull,
                                        capabilities=caps)
        self.wait = WebDriverWait(self.driver, 120)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.driver.quit()
        if self.parameters:
            with open(self.json_file_name, 'w', encoding='utf-8') as f:
                json.dump(self.parameters, f)

    def run(self):
        try:
            self._visit_dutchie()
        except:
            traceback.print_exc()
            return get_parameters_from_file()
        else:
            return self._extract_result()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, max=10))
    def _visit_dutchie(self):
        self.driver.get('https://dutchie.com/home')

        # Accept I'm over 21
        try:
            button = self.wait.until(EC.presence_of_element_located((By.XPATH,
                                                                     '//button[@data-cy="age-restriction-yes"]')))
            button.click()
        except:
            pass

        # Search one address
        search_input = self.wait.until(EC.presence_of_element_located((By.ID, 'auto-complete')))
        search_input.send_keys('Calgary,Alberta')
        time.sleep(1)
        search_btn = self.driver.find_element_by_xpath('//button[contains(concat(" ", '
                                                       'normalize-space(text()), " "), "Start Shopping")]')
        search_btn.click()
        time.sleep(2)

        # Select the first address in the list
        list_xpath = '//button[contains(@class, "places-list__ListContainer")]/li'
        self.wait.until(EC.element_to_be_clickable((By.XPATH, list_xpath)))
        list_items = self.driver.find_elements_by_xpath(list_xpath)
        list_items[0].click()
        time.sleep(1)

        # Manual visits
        self.driver.get('https://v3.dutchie.com/dispensary/spiritleaf-centre-st')
        time.sleep(5)
        self.driver.get('https://v3.dutchie.com/dispensary/spiritleaf-centre-st/products/flower')
        time.sleep(5)
        self.driver.get('https://v3.dutchie.com/dispensary/spiritleaf-centre-st/product/black-cherry-punch-1g')
        time.sleep(5)
        """# Click one shop
        links_xpath = '//ul[contains(@class, "dispensary-list__Container")]' \
                      '/li/a[contains(@class, "dispensary-card__Container")]'
        self.wait.until(EC.presence_of_element_located((By.XPATH, links_xpath)))
        links = self.driver.find_elements_by_xpath(links_xpath)
        url = links[0].get_attribute('href').replace('v3.dutchie.com/dispensary', 'dutchie.com/dispensaries')
        self.driver.get(url)
        self.wait.until(EC.presence_of_element_located((By.ID, 'products-container')))

        # Click one product
        links_xpath = '//div[contains(@class, "products-grid__ProductCardGrid")]/div' \
                      '/a[contains(@class, "consumer-product-card")]'
        self.wait.until(EC.element_to_be_clickable((By.XPATH, links_xpath)))
        links = self.driver.find_elements_by_xpath(links_xpath)
        # links[0].click()
        self.driver.execute_script("arguments[0].click();", links[0])
        time.sleep(2)"""

    def _extract_result(self) -> dict:
        for request in self.driver.requests:
            if 'operationName=DispensarySearch' in request.url:
                # print(request.url, request.headers)
                self.parameters['search_store_url'] = self._replace_query(request.url,
                                                                          {'nearLat': '{0}',
                                                                           'nearLng': '{1}',
                                                                           'destinationTaxState': '{2}'})
                self.parameters['search_store_headers'] = self._extract_headers(request.headers)
            elif 'operationName=ConsumerDispensaries' in request.url:
                # print(request.url, request.headers)
                self.parameters['search_address_url'] = self._replace_query(request.url,
                                                                            {'cNameOrID': '{0}'},
                                                                            ['city',
                                                                             'nearLat',
                                                                             'nearLng',
                                                                             'destinationTaxState'])
                self.parameters['search_address_headers'] = self._extract_headers(request.headers)
            elif 'operationName=FilteredProducts' in request.url and 'page' in request.url and 'perPage' in request.url:
                link_to_save = 'https://dutchie.com/graphql?operationName=FilteredProducts&variables={{"productsFilter":{{"dispensaryId":"{0}","bypassOnlineThresholds":false}},"page":0,"perPage":5000}}&extensions={{"persistedQuery":{{"version":1,"sha256Hash":"KEY"}}}}'
                key = json.loads(unquote(request.url.split('=')[-1]))['persistedQuery']['sha256Hash']
                link_to_save = link_to_save.replace('KEY', key)
                self.parameters['search_products_url'] = link_to_save
                self.parameters['search_products_headers'] = self._extract_headers(request.headers)
            elif 'operationName=FilteredProducts' in request.url:
                link_to_save = 'https://dutchie.com/graphql?operationName=FilteredProducts&variables={{"productsFilter":{{"productId":"{0}","bypassOnlineThresholds":false}},"hideEffects":false,"useCache":true}}&extensions={{"persistedQuery":{{"version":1,"sha256Hash":"KEY"}}}}'
                key = json.loads(unquote(request.url.split('=')[-1]))['persistedQuery']['sha256Hash']
                link_to_save = link_to_save.replace('KEY', key)
                # print(request.url, request.headers)
                self.parameters['search_details_url'] = link_to_save
                self.parameters['search_details_headers'] = self._extract_headers(request.headers)

        return self.parameters

    @staticmethod
    def _replace_query(url, new_queries: dict, pop_queries: Optional[list] = None) -> str:
        parsed = urlsplit(url)
        query_dict = parse_qs(parsed.query)
        if 'variables' not in query_dict:
            logging.error(str(query_dict))
            raise Exception('variables not in query_dict')

        variables = json.loads(query_dict['variables'][0])
        if 'dispensaryFilter' in variables:
            variables = variables['dispensaryFilter']
        elif 'productsFilter' in variables:
            variables = variables['productsFilter']
        else:
            logging.error(str(query_dict))
            raise Exception('Unsupported variables format')

        new_url = unquote(url).replace('{', '{{').replace('}', '}}')
        if pop_queries:
            for key_to_pop in pop_queries:
                if key_to_pop in variables:
                    variables.pop(key_to_pop)

            index1 = new_url.find('{{"dispensaryFilter"')
            index2 = new_url.find('}}}}', index1)
            new_filter = json.dumps({'dispensaryFilter': variables}).replace('{', '{{').replace('}', '}}')
            new_url = new_url.replace(new_url[index1: index2 + 4], new_filter)

        for key, new_value in new_queries.items():
            if key not in variables:
                continue
            new_url = new_url.replace(str(variables[key]), new_value)
            variables[key] = new_value
        return new_url

    @staticmethod
    def _extract_headers(headers: HTTPHeaders) -> dict:
        result = {}
        for one in headers.items():
            key, value = one
            if key != 'cookie' and key != 'referer':
                result[key] = value
        return result


def get_parameters_from_file() -> dict:
    if os.path.exists(BrowseDutchie.json_file_name):
        with open(BrowseDutchie.json_file_name, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        return {}


def get_parameters(proxy_url: Optional[str] = None) -> dict:
    with BrowseDutchie(proxy_url) as bd:
        return bd.run()


if __name__ == '__main__':
    get_parameters('http://127.0.0.1:24000')
