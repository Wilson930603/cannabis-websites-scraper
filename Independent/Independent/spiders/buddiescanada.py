from Independent.spiders.base_spider import BaseSpider
import scrapy


class BuddiescanadaScraper(BaseSpider):
	name = 'buddiescanada'
	headers = {
		'authority': 'buddiescanada.ca',
		'pragma': 'no-cache',
		'cache-control': 'no-cache',
		'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
		'sec-ch-ua-mobile': '?0',
		'upgrade-insecure-requests': '1',
		'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36',
		'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
		'sec-fetch-site': 'none',
		'sec-fetch-mode': 'navigate',
		'sec-fetch-user': '?1',
		'sec-fetch-dest': 'document',
		'accept-language': 'en-US,en;q=0.9,fr-FR;q=0.8,fr;q=0.7',
		'cookie': 'PHPSESSID=5e268fb1b98d660d68994a3656ca3796; mailchimp_landing_site=https%3A%2F%2Fbuddiescanada.ca%2Fwp-admin%2Fadmin-ajax.php; tve_leads_unique=1; tl_21220_21221_6=a%3A1%3A%7Bs%3A6%3A%22log_id%22%3BN%3B%7D; woocommerce_recently_viewed=4453; tlf_6=1; cf_chl_2=b42cd138f2263ce; cf_chl_prog=a8; cf_clearance=k_up.1.xLiZsDp.wQAz1D3s_VkC5Yj2hrfHWGm_NO.4-1631194777-0-150',
	}

	def start_requests(self):
		yield scrapy.Request('https://buddiescanada.ca/our-selection/', headers=self.headers, callback=self.parse)

	def parse(self, response):
		social = response.xpath('//a[@class="elementor-icon elementor-social-icon elementor-social-icon-instagram elementor-repeater-item-a1fa4b9"]/@href').get()
		email = response.xpath('//div[@data-id="457ce3a5"]/div/div/p[2]/span/text()[2]').get()
		print(social, email)
		categories = response.xpath('//ul[@class="products columns-3"]/li/a/@href').getall()
		for category_link in categories:
			pass
