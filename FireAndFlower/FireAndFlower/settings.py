# -*- coding: utf-8 -*-
from shutil import which
# Scrapy settings for FireAndFlower project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'FireAndFlower'

SPIDER_MODULES = ['FireAndFlower.spiders']
NEWSPIDER_MODULE = 'FireAndFlower.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:88.0) Gecko/20100101 Firefox/88.0'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    #'Accept-Encoding': 'gzip, deflate, br'
}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'FireAndFlower.middlewares.FireAndFlowerSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    # 'FireAndFlower.middlewares.ProxyMiddleware': 420,
    'FireAndFlower.middlewares.IncompleteRetryMiddleware': 450,
}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'FireAndFlower.pipelines.CSVPipeline': 300,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

RETRY_TIMES = 5
RETRY_HTTP_CODES = [408, 429, 452, 500, 502, 503, 504]
LOG_LEVEL = 'INFO'
LOG_FILE_PATH = './logs/'
LOG_ENABLED = True

PROXY_URL = 'http://127.0.0.1:24000'
DATA_FILE_PATH = './output/'
BRANDS = ['', 'RGB Cannabis', 'RGB', 'Stigma Grow', 'Candre Cannabis Inc.', 'Candre Cannabis', 'AGLC', 'BCCannabis', 'Stigma', 'RAD', 'Black NGL', 'White NGL', 'Chapter 1', 'Joi Botanicals', 'Joi', 'Dab Bods', 'Joi Botanical', 'Joi Botanicals Ltd.', 'Joi Botanicals Ltd', 'Pura Vida', 'Feel Good', 'Feel Good.', 'FeelGood', 'Premium 5', 'Premium5', 'Pure Farma', 'PureFarma', 'Purefarma', 'ArthroCBD', 'Arthro CBD', 'Really Awesome Dope', 'ACREAGE PHARMS LTD', 'Voyage Cannabis Corp', 'Edison', 'Shred', 'Shred''Ems', 'Trailblazer', 'Big Bag O Buds', 'Big Bag O'' Buds', 'Edison Cannabis Co.', 'Edison Cannabis', 'Edison Cannabis Co','Organigram', 'Emerald', 'Emerald Health', 'Sync', 'Sync Wellness', 'Fuse', 'Souvenir']
