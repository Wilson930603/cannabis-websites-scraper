from Independent.spiders.base_spider import BaseSpider
import scrapy
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.webdriver.chrome.options import Options

class PrairieSpider(BaseSpider):
    name = 'livingskiescannabis'
    allowed_domains = ['livingskiescannabis.ca']
    start_urls = ['https://www.tweed.com/']
    shop_name = 'Living Skies Cannabis'
    p_id = '990114'
    
    def parse(self, response):
        shops = [('https://livingskiescannabis.ca/downtown/', '990114', '208 3rd Avenue South, Saskatoon, SK, S7K 1M1', '306-343-9333', 'livingskies.ask@gmail.com'),
                 ('https://livingskiescannabis.ca/fairlight', '990115', '3322 Fairlight Drive, Saskatoon, SK, S7M 3Y4', '306-652-9333', 'livingskies.ask@gmail.com'),
                 ('https://livingskiescannabis.ca/millar', '990116', '116-2834 Millar Avenue, Saskatoon, SK, S7K 5X7', '306-373-9333', 'livingskies.ask@gmail.com'),
                 ('https://livingskiescannabis.ca/8th', '990117', '3501 8 Street East, Saskatoon, SK, S7H 0W5', '306-244-5874', 'livingskies.ask@gmail.com')]
        for shop in shops:
            website = shop[0]
            p_id = shop[1]
            full_address = shop[2]
            address = full_address.split(',')[0].strip()
            city = full_address.split(',')[1].strip()
            state = full_address.split(',')[2].strip()
            postal = full_address.split(',')[3].strip()
            phone = shop[3]
            email = shop[4]

            yield {
                "Producer ID": '',
                "p_id": p_id,
                "Producer": self.shop_name,
                "Description": '',
                "Link": website,
                "SKU": "",
                "City": city,
                "Province": state,
                "Store Name": self.shop_name,
                "Postal Code": postal,
                "long": '',
                "lat": '',
                "ccc": "",
                "Page Url": website,
                "Active": 'Yes',
                "Main image": 'https://livingskiescannabis.ca/wp-content/uploads/2018/10/image.png',
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
                "Social": '',
                "FullAddress": full_address,
                "Address": address,
                "Additional Info": "",
                "Created": "",
                "Comment": "",
                "Updated": ""
            }

        options = Options()
        # options.add_argument('--headless')
        # options.add_argument('--disable-gpu')
        browser = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)

        stores = [('-MEiSG50Ph19ghp5HTE-', '990114'), 
                  ('-MSK7c00Xl76Ivk8a3m2', '990115'),
                  ('-MSK69CyndJQVbbTSaOs', '990116'),
                  ('-MXhLkK-A1YuPciZB_2H', '990117')][:1]
        for store in stores:
            categories = [f'https://verda.com/stores/{store[0]}/collection/-MEiWW4xGTOTcsQij5ux',
                          f'https://verda.com/stores/{store[0]}/collection/-MEjBollhWfRJ7p21bsx',
                          f'https://verda.com/stores/{store[0]}/collection/-MEjDGOHWGUvAmEFjUc2',
                          f'https://verda.com/stores/{store[0]}/collection/-MEjDC90fBQ1M-9Uwgl-',
                          f'https://verda.com/stores/{store[0]}/collection/-MEjBvbfziTwXFYuTiZP',
                          f'https://verda.com/stores/{store[0]}/collection/-MEjBzFjoPL6X8l_Hsws',
                          f'https://verda.com/stores/{store[0]}/collection/-MEjDRzvVbaFY3JBVZjv',
                          f'https://verda.com/stores/{store[0]}/collection/-MEjDbJq4RnqGWPaUfrU',
                          f'https://verda.com/stores/{store[0]}/collection/-MEjDVGpLPKALTv3P1R8']

            for category in categories:
                browser.get(category)
                try:
                    WebDriverWait(browser, 5).until(EC.visibility_of_element_located((By.XPATH, '//button[@type="submit"]'))).click()
                except:
                    pass
                try:
                    WebDriverWait(browser, 20).until(EC.visibility_of_element_located((By.XPATH, '//div[@class="card-content"]')))
                except:
                    continue
                time.sleep(1)
                cards = browser.find_elements_by_xpath('//div[@class="card"]/a')
                
                links = []
                for card in cards:
                    url = card.get_attribute('href')
                    links.append(url)
                
                for url in links:
                    browser.get(url)
                    product_id = url.split('/')[-1]
                    try:
                        title = WebDriverWait(browser, 20).until(EC.visibility_of_element_located((By.XPATH, '//h1[@class="title is-2"]'))).text
                        content = WebDriverWait(browser, 20).until(EC.visibility_of_element_located((By.XPATH, '//div[@class="is-flex mb-4 has-flex-wrap product-header-wrapper"]'))).text
                        strain = content.split('STRAIN')[1].split('\n')[0].strip()
                        thc = content.split('THC')[1].split('\n')[0].strip()
                        cbd = content.split('CBD')[1].split('\n')[0].strip()
                        image = browser.find_element_by_xpath('//figure/img').get_attribute('src')
                        try:
                            description = browser.find_element_by_xpath('//p[@class="py-3"]').text
                        except:
                            description = ''
                        WebDriverWait(browser, 20).until(EC.visibility_of_element_located((By.XPATH, '//div[@class="border-bottom p-5 center-text-mobile"]')))
                        cards_ = browser.find_elements_by_xpath('//div[@class="border-bottom p-5 center-text-mobile"]')
                        brand = browser.find_element_by_xpath('//p[@class="subtitle is-5"]').text.split('-')[0].strip()
                        category = browser.find_element_by_xpath('//span[@class="tag is-primary is-medium"]').text
                        for card in cards_:
                            weight = WebDriverWait(card, 20).until(EC.visibility_of_element_located((By.XPATH, './/h1[@class="title is-size-2"]'))).text
                            price = WebDriverWait(card, 20).until(EC.visibility_of_element_located((By.XPATH, './/p[@class="subtitle is-size-3"]'))).text.replace('CAD $', '')
                            yield {
                                "Page URL": url,
                                "Brand": brand,
                                "Name": title,
                                "SKU": '',
                                "Out stock status": 'In Stock',
                                "Stock count": '',
                                "Currency": "CAD",
                                "ccc": "",
                                "Price": price,
                                "Manufacturer": self.shop_name,
                                "Main image": image,
                                "Description": description,
                                "Product ID": product_id.replace('=', '').replace('-', ''),
                                "Additional Information": '',
                                "Meta description": '',
                                "Meta title": '',
                                "Old Price": '',
                                "Equivalency Weights": '',
                                "Quantity": '',
                                "Weight": weight,
                                "Option": '',
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
                                "Sort order": '',
                                "Attribute 1": 'THC',
                                "Attribute Value 1": thc,
                                "Attribute 2": 'CBD',
                                "Attribute value 2": cbd,
                                "Attribute 3": 'Strain',
                                "Attribute value 3": strain,
                                "Attribute 4": '',
                                "Attribute value 4": '',
                                "Reviews": '',
                                "Review link": "",
                                "Rating": '',
                                "Address": '',
                                "p_id": store[1]
                            }
                    except Exception as err:
                        pass