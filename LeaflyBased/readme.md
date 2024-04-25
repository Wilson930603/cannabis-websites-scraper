# Deployment guide

1. Install Python 3.8

2. Create a virtual Python3 environment and activate it.

3. Install the required third-party libraries by running the command 

   ```
   pip install -r requirement.txt
   ```

4. Change the variable "PROXY_URL" in "settings.py" to your own proxy URL.

5. Change the variable "DATA_FILE_PATH" in "settings.py" to the path you want to store the CSV files.

6. Change the variable "BRAND" in "settings.py" to the brand names you want to include in the result. Leave it blank (BRANDS = []) will include all brands in the result.



# How to use the spider

2. cd to the project's root directory, e.g. 

   ```
   cd /codes/LeaflyBased
   ```

3. Activate the virtual Python3 environment.

3. Run the command 

   ```
   scrapy crawl {spider_name}
   ```

   or

   ```
   scrapy crawl {spider_name} -a city="{city_name}"
   ```

   e.g.

   ```
   scrapy crawl valuebuds -a city="Calgary"
   ```

   

# Spider names

| Spider name       | Website                                                      |
| ----------------- | ------------------------------------------------------------ |
| budaboom          | https://www.budaboom.com/                                    |
| microgoldcannabis | https://www.leafly.com/dispensary-info/micro-gold-cannabis-okotoks/menu |
| valuebuds         | https://valuebuds.com/pages/shop                             |
| prairierecords    | https://www.prairierecords.ca/pages/store-menus              |

| Spider name                         | Keyword                                                |
| ----------------------------------- | ------------------------------------------------------ |
| fivepoint_cannabis                  | FivePoint Cannabis Menu \| Leafly                      |
| canna_cabana_calgary_canyon_meadows | Canna Cabana - Calgary - Canyon Meadows Menu \| Leafly |
| spiritleaf_canyon_meadows           | Spiritleaf - Canyon Meadows Menu \| Leafly             |
| lake_city_cannabis                  | Lake City Cannabis Menu \| Leafly                      |
| spiritleaf_millrise                 | Spiritleaf - Millrise Menu \| Leafly                   |
| moderna_cannabis_society            | Moderna Cannabis Society Menu \| Leafly                |
| newleaf_cannabis_1st_ave            | NewLeaf Cannabis - 1st Ave Menu \| Leafly              |

