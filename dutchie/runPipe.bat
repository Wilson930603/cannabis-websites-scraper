cd C:\scripts\neobi-robots\dutchie
call .\neobi-dutchie\Scripts\activate

call scrapy crawl get_producers -a city=spruce_grove,Alberta -a update_params=True
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
call scrapy crawl get_producers -a city=whitecourt,Alberta -a update_params=False
timeout /t 5 /nobreak
call scrapy crawl get_products -a city=whitecourt,Alberta -a update_params=False
timeout /t 5 /nobreak

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
call scrapy crawl get_producers -a city=drayton_valley,Alberta -a update_params=False
timeout /t 5 /nobreak
call scrapy crawl get_products -a city=drayton_valley,Alberta -a update_params=False
timeout /t 10 /nobreak
timeout /t 1 /nobreak
call scrapy crawl get_producers -a city=brooks,Alberta -a update_params=False
timeout /t 5 /nobreak
call scrapy crawl get_products -a city=brooks,Alberta -a update_params=False
timeout /t 10 /nobreak

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

call scrapy crawl get_producers -a city=calgary,Alberta -a update_params=False
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

timeout /t 15 /nobreak
call scrapy crawl get_producers -a city=beaumont,Alberta -a update_params=False
timeout /t 5 /nobreak
call scrapy crawl get_products -a city=beaumont,Alberta -a update_params=False
timeout /t 15 /nobreak
call scrapy crawl get_producers -a city=irricana,Alberta -a update_params=False
timeout /t 5 /nobreak
call scrapy crawl get_products -a city=irricana,Alberta -a update_params=False
timeout /t 15 /nobreak
call scrapy crawl get_producers -a city=beiseker,Alberta -a update_params=False
timeout /t 5 /nobreak
call scrapy crawl get_products -a city=beiseker,Alberta -a update_params=False
timeout /t 15 /nobreak
call scrapy crawl get_producers -a city=vegreville,Alberta -a update_params=False
timeout /t 5 /nobreak
call scrapy crawl get_products -a city=vegreville,Alberta -a update_params=False
