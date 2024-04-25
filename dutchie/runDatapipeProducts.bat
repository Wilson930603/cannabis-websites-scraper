cd C:\scripts\neobi-robots\dutchie
call .\neobi-dutchie\Scripts\activate
call scrapy crawl get_products -a city=camrose,Alberta -a update_params=False
timeout /t 20 /nobreak
call scrapy crawl get_products -a city=chestermere,Alberta -a update_params=False
timeout /t 35 /nobreak
call scrapy crawl get_products -a city=cold_lake,Alberta -a update_params=False
timeout /t 125 /nobreak
call scrapy crawl get_products -a city=st_albert,Alberta -a update_params=False
timeout /t 15 /nobreak
call scrapy crawl get_products -a city=grande_prairie,Alberta -a update_params=False
timeout /t 2 /nobreak
call scrapy crawl get_products -a city=lacombe,Alberta -a update_params=False
timeout /t 20 /nobreak
call scrapy crawl get_products -a city=lethbridge,Alberta -a update_params=False
timeout /t 1 /nobreak
call scrapy crawl get_products -a city=fort_saskatchewan,Alberta -a update_params=False
timeout /t 1 /nobreak
call scrapy crawl get_products -a city=peace_river,Alberta -a update_params=False
timeout /t 10 /nobreak
call scrapy crawl get_products -a city=brooks,Alberta -a update_params=False
timeout /t 100 /nobreak
call scrapy crawl get_products -a city=lloydminster,Alberta -a update_params=False
timeout /t 20 /nobreak
call scrapy crawl get_products -a city=medicine_hat,Alberta -a update_params=False
timeout /t 10 /nobreak
call scrapy crawl get_products -a city=red_deer,Alberta -a update_params=False
timeout /t 55 /nobreak
call scrapy crawl get_products -a city=leduc,Alberta -a update_params=False
timeout /t 5 /nobreak
call scrapy crawl get_products -a city=jasper,Alberta -a update_params=False
timeout /t 5 /nobreak
call scrapy crawl get_products -a city=drumheller,Alberta -a update_params=False
timeout /t 50 /nobreak
call scrapy crawl get_products -a city=spruce_grove,Alberta -a update_params=False
timeout /t 12 /nobreak
call scrapy crawl get_products -a city=wetaskiwin,Alberta -a update_params=False
timeout /t 90 /nobreak
call scrapy crawl get_products -a city=Airdrie,Alberta -a update_params=False
timeout /t 3 /nobreak
call scrapy crawl get_products -a city=banff,Alberta -a update_params=False
timeout /t 8 /nobreak
call scrapy crawl get_products -a city=fort_mcmurray,Alberta -a update_params=False
timeout /t 17 /nobreak
call scrapy crawl get_products -a city=hinton,Alberta -a update_params=False