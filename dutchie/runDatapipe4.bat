cd C:\scripts\neobi-robots\dutchie
call .\neobi-dutchie\Scripts\activate
call scrapy crawl get_producers -a city=lloydminster,Alberta -a update_params=False
timeout /t 10 /nobreak
call scrapy crawl get_products -a city=lloydminster,Alberta -a update_params=False
timeout /t 20 /nobreak
call scrapy crawl get_producers -a city=medicine_hat,Alberta -a update_params=False
timeout /t 15 /nobreak
call scrapy crawl get_products -a city=medicine_hat,Alberta -a update_params=False
timeout /t 10 /nobreak
call scrapy crawl get_producers -a city=red_deer,Alberta -a update_params=False
timeout /t 5 /nobreak
call scrapy crawl get_products -a city=red_deer,Alberta -a update_params=False
timeout /t 5 /nobreak
call scrapy crawl get_producers -a city=leduc,Alberta -a update_params=False
timeout /t 5 /nobreak
call scrapy crawl get_products -a city=leduc,Alberta -a update_params=False
timeout /t 5 /nobreak
call scrapy crawl get_producers -a city=jasper,Alberta -a update_params=False
timeout /t 5 /nobreak
call scrapy crawl get_products -a city=jasper,Alberta -a update_params=False
timeout /t 5 /nobreak
call scrapy crawl get_producers -a city=drumheller,Alberta -a update_params=False
timeout /t 5 /nobreak
call scrapy crawl get_products -a city=drumheller,Alberta -a update_params=False
timeout /t 5 /nobreak
