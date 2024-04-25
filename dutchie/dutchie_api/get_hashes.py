import os
import time
from typing import Optional
import requests as r

from selenium.webdriver import DesiredCapabilities
from tenacity import retry, stop_after_attempt, wait_exponential
from seleniumwire import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


class BrowseDutchie:
    hashes = {}

    def __init__(self, proxy_url=None):
        self.proxy_url = proxy_url
        self.parameters = {}

    def __enter__(self):
        firefox_options = webdriver.FirefoxOptions()
        # firefox_options.headless = True
        firefox_options.set_preference("dom.webdriver.enabled", False)
        firefox_options.set_preference("useAutomationExtension", False)
        caps = DesiredCapabilities.FIREFOX.copy()
        self.driver = webdriver.Firefox(options=firefox_options,
                                        seleniumwire_options=None,
                                        service_log_path=os.devnull,
                                        capabilities=caps)
        self.wait = WebDriverWait(self.driver, 120)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.driver.quit()
        print(self.hashes)
        if self.hashes:
            res = r.get(f'http://3.144.196.137:1240/save?DispensarySearchHash={self.hashes["DispensarySearchHash"]}&DispensaryHash={self.hashes["DispensaryHash"]}&ProductHash={self.hashes["ProductHash"]}&ProductHashWithDetails={self.hashes["ProductHashWithDetails"]}&SpecialHash={self.hashes["SpecialHash"]}')
            print(res.json())

    def run(self):
        self._visit_dutchie()
        return self._extract_result()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, max=10))
    def _visit_dutchie(self):
        self.driver.get('https://dutchie.com/')
        try:
            button = self.wait.until(EC.presence_of_element_located((By.XPATH, '//button[@data-cy="age-restriction-yes"]')))
            button.click()
        except:
            try:
                field = self.driver.find_element_by_xpath('//input[@class="MuiInputBase-input MuiOutlinedInput-input"]')
                field.send_keys('11/11/1990')
                self.driver.find_element_by_xpath('//button[@class="button__StyledButton-nsdkri-1 bqgOFZ"]').click()
                time.sleep(5)
            except Exception as e:
                print(e)
                pass
        search_input = self.wait.until(EC.presence_of_element_located((By.ID, 'auto-complete')))
        search_input.send_keys('Calgary,Alberta')
        time.sleep(1)
        search_btn = self.driver.find_element_by_xpath('//li[@class="address-suggestion__Container-sc-1j7og5j-0 jIAxhW"]')
        search_btn.click()
        time.sleep(2)
        self.driver.get('https://dutchie.com/dispensary/mr-nice-guy-portland-se-woodstock/products/flower')
        time.sleep(5)
        self.driver.get('https://dutchie.com/dispensary/mr-nice-guy-portland-se-woodstock/product/apple-fritter')
        time.sleep(5)

    def _extract_result(self) -> dict:
        for request in self.driver.requests:
            if 'operationName=DispensarySearch' in request.url:
                dispensary_search_hash = request.url.split('sha256Hash%22%3A%22')[1].split('%22')[0]
                self.hashes['DispensarySearchHash'] = dispensary_search_hash
            elif 'operationName=ConsumerDispensaries' in request.url:
                dispensary_hash = request.url.split('sha256Hash%22%3A%22')[1].split('%22')[0]
                self.hashes['DispensaryHash'] = dispensary_hash
            elif 'operationName=FilteredProducts' in request.url and 'cName' in request.url:
                product_hash = request.url.split('sha256Hash%22%3A%22')[1].split('%22')[0]
                self.hashes['ProductHashWithDetails'] = product_hash
            elif 'operationName=FilteredProducts' in request.url:
                product_hash = request.url.split('sha256Hash%22%3A%22')[1].split('%22')[0]
                self.hashes['ProductHash'] = product_hash
            elif 'operationName=FilteredSpecials' in request.url:
                product_hash = request.url.split('sha256Hash%22%3A%22')[1].split('%22')[0]
                self.hashes['SpecialHash'] = product_hash


def get_parameters(proxy_url: Optional[str] = None) -> dict:
    with BrowseDutchie(proxy_url) as bd:
        return bd.run()


if __name__ == '__main__':
    get_parameters()
