# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from scrapy.exporters import CsvItemExporter
import os
import datetime


class CSVPipeline:
    def open_spider(self, spider):
        today_date = datetime.date.today().strftime("%m-%d-%y")
        full_path = f'{spider.settings.get("DATA_FILE_PATH")}/{today_date}'
        try:
            os.mkdir(full_path)
        except:
            pass
        if spider.name == 'get_products':
            file_path = f'{full_path}/Products_{spider.city} (dutchie).csv'
        elif spider.name == 'get_producers':
            file_path = f'{full_path}/Producers_{spider.city} (dutchie).csv'
            self.p_ids = set()
            self.producer_id = 0
        elif spider.name == 'get_updates':
            file_path = f'{full_path}/Updates_{spider.city} (dutchie).csv'
        else:
            raise Exception(f'Unsupported spider {spider.name}')

        self.file = open(file_path, 'wb')
        self.exporter = CsvItemExporter(self.file, include_headers_line=True, encoding='utf-8')
        if spider.name == 'get_products':
            self.exporter.fields_to_export = [
                "Producer_ID", "Page_URL", "Brand", "Name", "SKU", "Out_stock_status", "Currency", "ccc", "Price",
                "Manufacturer", "Main_image", "Description", "Product_ID", "Additional_Information", "Meta_description",
                "Meta_title", "Old_Price", "Equivalency_Weights", "Quantity", "Weight", "Option", "Option_type",
                "Option_Value", "Option_image", "Option_price_prefix", "Cat_tree_1_parent", "Cat_tree_1_level_1",
                "Cat_tree_1_level_2", "Cat_tree_2_parent", "Cat_tree_2_level_1", "Cat_tree_2_level_2",
                "Cat_tree_2_level_3", "Image_2", "Image_3", "Image_4", "Image_5", "Sort_order", "Attribute_1",
                "Attribute_Value_1", "Attribute_2", "Attribute_value_2", "Attribute_3", "Attribute_value_3",
                "Attribute_4", "Attribute_value_4", "Reviews", "Review_link", "Rating"
            ]
        elif spider.name == 'get_updates':
            self.exporter.fields_to_export = [
                "Producer ID", "Product ID", "Product Name", "Stock Count", "Product Price"
            ]
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        if spider.name == 'get_producers':
            if item['p_id'] not in self.p_ids:
                item['Producer ID'] = self.producer_id
                self.exporter.export_item(item)
                self.producer_id += 1
                self.p_ids.add(item['p_id'])
        elif spider.name == 'get_products':
            self.exporter.export_item(item)
        elif spider.name == 'get_updates':
            self.exporter.export_item(item)
        return item


class AllInOneCSVPipeline:
    def open_spider(self, spider):
        today_date = datetime.date.today().strftime("%m-%d-%y")
        full_path = f'{spider.settings.get("DATA_FILE_PATH")}/{today_date}'
        try:
            os.mkdir(full_path)
        except:
            pass
        self.p_ids = set()
        self.producer_id = 0
        file_path_producer = f'{full_path}/{spider.name}_Producer (dutchie).csv'
        self.file_producer = open(file_path_producer, 'wb')
        self.exporter_producer = CsvItemExporter(self.file_producer, include_headers_line=True, encoding='utf-8-sig')
        self.exporter_producer.start_exporting()

        file_path_products = f'{full_path}/{spider.name}_Products (dutchie).csv'
        self.file_products = open(file_path_products, 'wb')
        self.exporter_products = CsvItemExporter(self.file_products, include_headers_line=True, encoding='utf-8-sig')
        self.exporter_products.start_exporting()

    def close_spider(self, spider):
        self.exporter_producer.finish_exporting()
        self.file_producer.close()

        self.exporter_products.finish_exporting()
        self.file_products.close()

    def process_item(self, item, spider):
        if 'Page URL' in item:
            self.exporter_products.export_item(item)
        else:
            if item['p_id'] not in self.p_ids:
                item['Producer ID'] = self.producer_id
                self.exporter_producer.export_item(item)
                self.producer_id += 1
                self.p_ids.add(item['p_id'])
        return item
