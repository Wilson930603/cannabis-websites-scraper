# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import logging

from scrapy.downloadermiddlewares.retry import RetryMiddleware


class PersistedQueryNotFoundRetryMiddleware(RetryMiddleware):

    def process_response(self, request, response, spider):
        if hasattr(response, 'text') and response.text is not None:
            if not response.text:
                reason = 'Empty response'
                logging.warning(f"{reason}: {request.url}")
                return self._retry(request, reason, spider) or response
            elif '{"message":"PersistedQueryNotFound"}' in response.text:
                reason = 'PersistedQueryNotFound'
                logging.warning(f"{reason}: {request.url} {request.meta.get('retry_times', 0)}")
                return self._retry(request, reason, spider) or response
        return response


class ProxyMiddleware:

    def process_request(self, request, spider):
        if 'dont_proxy' in request.meta and request.meta['dont_proxy']:
            return
        if 'proxy' in request.meta and request.meta['proxy']:
            return
        if not spider.settings.get('PROXY_URL'):
            return

        request.meta['proxy'] = spider.settings.get('PROXY_URL')
