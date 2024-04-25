from Independent.spiders.base_spider import BaseSpider
import scrapy
import requests as r
import re

class HotBoxSpider(BaseSpider):
    name = 'hotbox'
    shops = {
		'241050': 'https://hotboxshop.ca/stores/ON/toronto-augusta-ave-kensington-market',
        '241051': 'https://hotboxshop.ca/stores/ON/toronto-augusta-ave-the-lounge',
	}
    shop_name = 'HotBox'
    img = 'https://ca.cdn.hifyreretail.com/130007/20210824/8379b95cd82642f1ae66c2c83f8efe8f'
    email = 'info@hotboxshop.ca'

    def start_requests(self):
        for shop_pid in self.shops:
            print(shop_pid)
            url = f'https://hotboxshop.ca/shop/{shop_pid}?redirect=%2Fshop'
            res = r.get(url)
            cookies = ''
            for cookie in res.cookies:
                cookies += f'{cookie.name}={cookie.value}; '
            yield scrapy.Request(self.shops[shop_pid], headers={'cookie': cookies}, callback=self.parse_store, dont_filter=True, meta={'p_id': shop_pid, 'cookies': cookies})

    def parse_store(self, response):
        p_id = response.meta['p_id']
        cookies = response.meta['cookies']
        full_addr = response.xpath('//div[@class="location-page--address"]/p[1]/text()').getall()
        addr = full_addr[0].strip().rstrip()
        city, province = full_addr[1].strip().rstrip().split(', ')
        postal_code = full_addr[2].strip().rstrip()
        phone = response.xpath('//div[@class="location-page--contact"]/a/text()').get()
        lat, lng = response.xpath('//div[@class="location-page--interactions"]/a/@href').get().split('/')[-1].split(',')
        social = '|'.join(response.xpath('//div[@class="ecom--secondary-footer--grid"]/div[2]/a/@href').getall())
        shop_item = {
            "Producer ID": '',
            "p_id": p_id,
            "Producer": f"{self.shop_name} - {city}",
            "Description": "",
            "Link": response.url,
            "SKU": "",
            "City": city,
            "Province": province,
            "Store Name": self.shop_name,
            "Postal Code": postal_code,
            "long": lng,
            "lat": lat,
            "ccc": "",
            "Page Url": response.url,
            "Active": "",
            "Main image": self.img,
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
            "Email": self.email,
            "Social": social,
            "FullAddress": "",
            "Address": addr,
            "Additional Info": "",
            "Created": "",
            "Comment": "",
            "Updated": ""
        }
        yield shop_item
        brands = '^'.join(self.settings.get('BRANDS', []))
        page = 1
        base_link = f'https://hotboxshop.ca/shop?q={brands}'

        yield scrapy.Request(base_link, meta={'p_id': p_id, 'cookies': cookies, 'page': page, 'base_link': base_link}, headers={'cookie': cookies}, callback=self.parse_menu, dont_filter=True)

    def parse_menu(self, response):
        print(response.url)
        p_id = response.meta['p_id']
        page = response.meta['page'] + 1
        base_link = response.meta['base_link']
        cookies = response.meta['cookies']
        product_ids = response.xpath('//button[@phx-value-product_id]/@phx-value-product_id').getall()
        print(product_ids)
        for product_id in product_ids:
        	yield scrapy.Request(f'https://hotboxshop.ca/products/{product_id}', dont_filter=True, callback=self.parse_product, meta={'p_id': p_id, 'product_id': product_id, 'cookies': cookies}, headers={'cookie': cookies})
        if product_ids:
            link = f'{base_link}&page={page}'
            yield scrapy.Request(link, dont_filter=True, callback=self.parse_menu, meta={'p_id': p_id, 'page': page, 'base_link': base_link, 'cookies': cookies}, headers={'cookie': cookies})

    def parse_product(self, response):
        print(response.url)
        brand = ''
        try:
            brand = re.search('var prodBrand =.+', response.text).group(0).split('"')[1]
        except:
            pass
        p_id = response.meta['p_id']
        product_id = response.meta['product_id']
        link = response.url
        name = response.xpath('//div[@class="product-page--title-rating"]/h1/text()').get()
        nb_reviews = response.xpath('//a[@id="review-scroller"]/text()').get()
        if nb_reviews:
            nb_reviews = nb_reviews.replace('Reviews', '').strip().rstrip()
        main_img = response.xpath('//div[@class="product-page--product-image"]/div/@data-bg').get()
        images = ['', '', '', '', '']
        if not main_img:
            main_img = response.xpath('//div[@class="image-slideshow--slide-wrapper"]/img[1]/@src').getall()
            for i in range(0, min(len(main_img), 5)):
                images[i] = main_img[i]
        else:
            images[0] = main_img
        stock = 'In Stock'
        out_stock = response.xpath('//div[@phx-hook="OtherStoresScroll"]/div/span/b/text()').get()
        stock_count = 0
        if out_stock:
            if 'Sold Out' in out_stock:
                stock = 'Out of Stock'
        else:
            stock_count = response.xpath('//div[@class="stock-message round-corners p-1 d-flex align-c justify-c mt-1 bg-warning-light border-warning"]/span/text()').get()
            if stock_count:
                stock_count = int(stock_count.strip().rstrip().replace('Only ', '').replace(' in stock', ''))
            else:
                stock_count = 10
        old_price = ''
        price = response.xpath('//span[@class="price bold"]/text()').get()
        if price:
            price = price.replace('$', '').strip().rstrip()
        else:
            old_price = response.xpath('//span[@class="price line-through muted regular"]/text()').get().replace('$', '').strip().rstrip()
            price = response.xpath('//p[@class="price bold brand m-0 d-flex fd-column justify-c"]/text()[2]').get().replace('$', '').strip().rstrip()
        thc = ''
        cbd = ''
        thc_name = ''
        cbd_name = ''
        boxes = response.xpath('//div[@class="bg-gray-light round-corners p-1 d-flex align-c flex-1"]')
        for box in boxes:
            title = box.xpath('./p/text()').get().strip().rstrip()
            value = box.xpath('./span/text()').get().strip().rstrip()
            if title == 'THC':
                thc_name = 'THC'
                thc = value
            elif title == 'CBD':
                cbd_name = 'CBD'
                cbd = value
        sku = ''
        try:
            sku = re.search('var prodSKU =.+', response.text).group(0).split('"')[1]
        except:
            pass
        rating = ''
        try:
            rating = re.search('var prodRating =.+', response.text).group(0).split('"')[1]
        except:
            pass
        options = response.xpath('//select[@id="product_variation_id"]/option/text()').getall()
        first_option = options[0] if ('ml' in options[0].lower() or 'gm' in options[0].lower() or '×' in options[0]) and len(options[0]) < 14 else ''
        cols = response.xpath('//li[@class="product-details--list-item"]')
        desc = ''
        for col in cols:
            header = col.xpath('./h3/text()').get()
            if 'DESCRIPTION' in header:
                desc = col.xpath('./p/text()').get()
                if desc:
                    desc = desc.strip().rstrip()
                break
        try:
            desc = desc.replace('\n', ' ').replace('\r', '').strip()
        except:
            pass

        item = {
            "Page URL": link,
            "Brand": brand,
            "Name": name,
            "SKU": sku,
            "Out stock status": stock,
            "Stock count": stock_count,
            "Currency": "CAD",
            "ccc": "",
            "Price": price,
            "Manufacturer": self.shop_name,
            "Main image": images[0],
            "Description": desc,
            "Product ID": product_id,
            "Additional Information": '',
            "Meta description": "",
            "Meta title": "",
            "Old Price": old_price,
            "Equivalency Weights": '',
            "Quantity": "",
            "Weight": first_option,
            "Option": "",
            "Option type": '',
            "Option Value": "",
            "Option image": "",
            "Option price prefix": "",
            "Cat tree 1 parent": "",
            "Cat tree 1 level 1": "",
            "Cat tree 1 level 2": "",
            "Cat tree 2 parent": '',
            "Cat tree 2 level 1": "",
            "Cat tree 2 level 2": "",
            "Cat tree 2 level 3": "",
            "Image 2": images[1],
            "Image 3": images[2],
            "Image 4": images[3],
            "Image 5": images[4],
            "Sort order": "",
            "Attribute 1": cbd_name,
            "Attribute Value 1": cbd,
            "Attribute 2": thc_name,
            "Attribute value 2": thc,
            "Attribute 3": "",
            "Attribute value 3": '',
            "Attribute 4": "",
            "Attribute value 4": "",
            "Reviews": nb_reviews,
            "Review link": "",
            "Rating": rating,
            "Address": '',
            "p_id": p_id
        }

        yield item
