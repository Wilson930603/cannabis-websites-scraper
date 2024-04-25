from rotating_proxies.policy import BanDetectionPolicy


class MyBanPolicy(BanDetectionPolicy):
    def response_is_ban(self, request, response):
        ban = super(MyBanPolicy, self).response_is_ban(request, response)
        return ban or response.status == 406

    def exception_is_ban(self, request, exception):
        return None
