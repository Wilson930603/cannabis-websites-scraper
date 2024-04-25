cd C:\scripts\neobi-robots\dutchie
call .\neobi-dutchie\Scripts\activate
call scrapy crawl get_producers -a city=camrose,Alberta -a update_params=False
timeout /t 20 /nobreak
call scrapy crawl get_products -a city=camrose,Alberta -a update_params=False
timeout /t 20 /nobreak
call scrapy crawl get_producers -a city=chestermere,Alberta -a update_params=False
timeout /t 10 /nobreak
call scrapy crawl get_products -a city=chestermere,Alberta -a update_params=False
timeout /t 5 /nobreak
call scrapy crawl get_producers -a city=cold_lake,Alberta -a update_params=False
timeout /t 10 /nobreak
call scrapy crawl get_products -a city=cold_lake,Alberta -a update_params=False
timeout /t 15 /nobreak
call scrapy crawl get_producers -a city=st_albert,Alberta -a update_params=False
timeout /t 30 /nobreak
call scrapy crawl get_products -a city=st_albert,Alberta -a update_params=False
timeout /t 15 /nobreak

