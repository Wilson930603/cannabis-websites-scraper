cd C:\scripts\python\dutchie_v2\dutchie\
call .\neobi-dutchie\Scripts\activate
call scrapy crawl get_producers -a city=calgary,Alberta -a update_params=True
timeout /t 10 /nobreak
call scrapy crawl get_products -a city=calgary,Alberta -a update_params=False
timeout /t 20 /nobreak
call scrapy crawl get_producers -a city=edmonton,Alberta -a update_params=False
timeout /t 10 /nobreak
call scrapy crawl get_products -a city=edmonton,Alberta -a update_params=False
timeout /t 15 /nobreak
call scrapy crawl get_producers -a city=brooks,Alberta -a update_params=False
timeout /t 5 /nobreak
call scrapy crawl get_products -a city=brooks,Alberta -a update_params=False
cd C:\scripts\Neobi.Brain\publish
dotnet Neobi.Brain.dll 19

