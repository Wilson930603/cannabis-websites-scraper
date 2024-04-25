cd C:\scripts\neobi-robots\dutchie
call .\neobi-dutchie\Scripts\activate
call scrapy crawl get_producers -a city=grande_prairie,Alberta -a update_params=False
timeout /t 15 /nobreak
call scrapy crawl get_products -a city=grande_prairie,Alberta -a update_params=False
timeout /t 2 /nobreak
call scrapy crawl get_producers -a city=lacombe,Alberta -a update_params=False
timeout /t 1 /nobreak
call scrapy crawl get_products -a city=lacombe,Alberta -a update_params=False
timeout /t 20 /nobreak
call scrapy crawl get_producers -a city=lethbridge,Alberta -a update_params=False
timeout /t 10 /nobreak
call scrapy crawl get_products -a city=lethbridge,Alberta -a update_params=False
timeout /t 1 /nobreak
call scrapy crawl get_producers -a city=fort_saskatchewan,Alberta -a update_params=False
timeout /t 5 /nobreak
call scrapy crawl get_products -a city=fort_saskatchewan,Alberta -a update_params=False
timeout /t 1 /nobreak
call scrapy crawl get_producers -a city=peace_river,Alberta -a update_params=False
timeout /t 5 /nobreak
call scrapy crawl get_products -a city=peace_river,Alberta -a update_params=False
timeout /t 10 /nobreak
timeout /t 1 /nobreak
call scrapy crawl get_producers -a city=brooks,Alberta -a update_params=False
timeout /t 5 /nobreak
call scrapy crawl get_products -a city=brooks,Alberta -a update_params=False
timeout /t 10 /nobreak