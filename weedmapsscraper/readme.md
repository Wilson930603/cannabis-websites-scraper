# Deployment guide

1. Install Python 3.8

2. Create a virtual Python3 environment and activate it.

3. Activate the virtual Python3 environment.

4. Install the required third-party libraries by running the command 

   ```
   pip install -r requirement.txt
   ```

5. Change the variable "PROXY_URL" in "settings.py" to your own proxy URL.

6. Change the variable "DATA_FILE_PATH" in "settings.py" to the path you want to store the CSV files.

7. Change the variable "BRAND" in "settings.py" to the brand names you want to include in the result. Leave it blank (BRANDS = []) will include all brands in the result.



# How to use the spider

2. cd to the project's root directory, e.g. 

   ```
   cd /codes/weedmapsscraper
   ```

3. Run the command 

   ```
   scrapy crawl weedmaps -a city=city_name -a province=province_code
   ```

Example:   

   ```
   scrapy crawl weedmaps -a city=calgary -a province=AB
   ```
