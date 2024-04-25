# Deployment guide

1. Install Python 3.8

2. Create a virtual Python3 environment and activate it. e.g.:

   ```
   python3 -m venv .venv
   .venv\Scripts\activate.bat
   ```

3. Install the required third-party libraries:

   ```
   pip install -r requirement.txt
   ```

4. Download Geckodriver(https://github.com/mozilla/geckodriver/) and place it somewhere on your PATH. (e.g.: C:\Windows)

5. Verify Geckodriver installation. Open a command window and run:
   ```
   geckodriver -V
   ```
   If there are no errors, and you can see the version number, then it's correctly installed.

6. Install Firefox

7. Change the variable "DATA_FILE_PATH" in "settings.py" to the path where you want to store the result CSV files. 
   e.g.:
   ```
   DATA_FILE_PATH = "D:\\data\\dutchie"
   ```
   
8. Change the variable "PROXY_URL" in "settings.py" to your own Luminati proxy URL.




# How to use the spider

1. cd to the project's root directory, e.g. 

   ```
   cd d:\codes\dutchie
   ```

3. Activate the virtual Python3 environment. e.g.:

   ```
   .venv\Scripts\activate.bat
   ```

4. The spider "get_producers" has two parameters: "city" and "update_params".
   
   "update_params" means whether to use Firefox to get new API parameters from dutchie.com. 
   Its default value is "True", which means if you don't pass this parameter then the spider will update 
   the duchie API parameters by default. 
   
   If "update_params" is set to True, the spider will use Firefox in headless mode to get the newest dutchie API parameters and store the result in the file "api_parameters.json".
   
   If "update_params" is set to False, the spider will use the API parameters from last time (values from the file "api_parameters.json").
   
   e.g.:
   
   Run the spider and update the dutchie API parameters:
   ```
   scrapy crawl get_producers -a city=Lloydminster,Alberta
   ```
   The above command is equivalent to the following one:
   ```
   scrapy crawl get_producers -a city=Lloydminster,Alberta -a update_params=True
   ```
   Run the spider and use the dutchie API parameters from last time:
   ```
   scrapy crawl get_producers -a city=Lloydminster,Alberta -a update_params=False
   ```
   
5. The spider "get_products" has the same parameters as "get_producers". 
   
   So, if you don't pass and set "update_params" to "False", it'll also use Firefox to get the newest dutchie API parameters.
