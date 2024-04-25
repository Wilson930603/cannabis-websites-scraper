from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep


options = webdriver.ChromeOptions()
#options.add_argument("window-size=1280,800")
#options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36")
options.add_argument('--disable-translate')
options.add_argument("--lang=en")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument('--disable-blink-features=AutomationControlled')
browser = webdriver.Chrome(executable_path="chromedriver.exe", options=options)
browser.get('https://fireandflower.com/stores')
sleep(5)
browser.find_element_by_id('age_gate_day').send_keys('2')
browser.find_element_by_id('age_gate_month').send_keys('1')
browser.find_element_by_id('age_gate_year').send_keys('1990')
browser.find_element_by_id('age_gate_year').send_keys(Keys.ENTER)
sleep(5)
WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, "//button[@class='btn btn-link underline uppercase muted']"))).click()
sleep(5)
sleep(300)
browser.quit()
