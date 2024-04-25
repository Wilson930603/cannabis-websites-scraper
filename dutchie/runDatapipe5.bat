cd C:\scripts\neobi-robots\dutchie
call .\neobi-dutchie\Scripts\activate
call scrapy crawl get_producers -a city=spruce_grove,Alberta -a update_params=False
timeout /t 10 /nobreak
call scrapy crawl get_products -a city=spruce_grove,Alberta -a update_params=False
timeout /t 12 /nobreak
call scrapy crawl get_producers -a city=wetaskiwin,Alberta -a update_params=False
timeout /t 11 /nobreak
call scrapy crawl get_products -a city=wetaskiwin,Alberta -a update_params=False
timeout /t 9 /nobreak
call scrapy crawl get_producers -a city=Airdrie,Alberta -a update_params=False
timeout /t 18 /nobreak
call scrapy crawl get_products -a city=Airdrie,Alberta -a update_params=False
timeout /t 3 /nobreak
call scrapy crawl get_producers -a city=banff,Alberta -a update_params=False
timeout /t 18 /nobreak
call scrapy crawl get_products -a city=banff,Alberta -a update_params=False
timeout /t 8 /nobreak
call scrapy crawl get_producers -a city=fort_mcmurray,Alberta -a update_params=False
timeout /t 7 /nobreak
call scrapy crawl get_products -a city=fort_mcmurray,Alberta -a update_params=False
timeout /t 7 /nobreak
call scrapy crawl get_producers -a city=hinton,Alberta -a update_params=False
timeout /t 7 /nobreak
call scrapy crawl get_products -a city=hinton,Alberta -a update_params=False