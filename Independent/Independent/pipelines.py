# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.exceptions import DropItem
from scrapy.exporters import CsvItemExporter
import os
import datetime


class CSVPipeline:
    def open_spider(self, spider):
        self.brands = [x.lower() for x in spider.settings.get('BRANDS', [])]
        self.p_ids = set()
        self.producer_id = 0
        today_date = datetime.date.today().strftime("%m-%d-%y")
        full_path = f'{spider.settings.get("DATA_FILE_PATH")}/{today_date}'
        try:
            os.mkdir(full_path)
        except:
            pass
        file_path_producer = f'{full_path}/{spider.name}_Producer.csv'
        self.file_producer = open(file_path_producer, 'wb')
        self.exporter_producer = CsvItemExporter(self.file_producer, include_headers_line=True, encoding='utf-8-sig')
        self.exporter_producer.start_exporting()

        file_path_products = f'{full_path}/{spider.name}_Products.csv'
        self.file_products = open(file_path_products, 'wb')
        self.exporter_products = CsvItemExporter(self.file_products, include_headers_line=True, encoding='utf-8-sig')
        self.exporter_products.start_exporting()

        self.url_pid_filter = set()

    def close_spider(self, spider):
        self.exporter_producer.finish_exporting()
        self.file_producer.close()

        self.exporter_products.finish_exporting()
        self.file_products.close()

    def process_item(self, item, spider):
        if 'Page URL' in item:
            if item['Brand'] and self.brands and item['Brand'].lower() not in self.brands:
                self.logger.debug(f'Ignore brand: {item["Brand"]}')
            else:
                url = item["Page URL"]
                if 'thejointcannabis.ca' in url:
                    url_pid = f'{url}_{item["p_id"]}'
                    if url_pid not in self.url_pid_filter:
                        self.url_pid_filter.add(url_pid)
                        self.exporter_products.export_item(item)
                    else:
                        raise DropItem()
                else:
                    self.exporter_products.export_item(item)
        else:
            if item['p_id'] not in self.p_ids:
                item['Producer ID'] = self.producer_id
                self.exporter_producer.export_item(item)
                self.producer_id += 1
                self.p_ids.add(item['p_id'])
        return item
