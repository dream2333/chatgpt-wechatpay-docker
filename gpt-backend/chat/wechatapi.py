import aiohttp


class WeChatAPI:
    async def init(self, appid, secret):
        self.appid = appid
        self.secret = secret
        self.session = aiohttp.ClientSession()

    async def get_access_token(self, code):
        """获取登录授权码"""
        api = f"https://api.weixin.qq.com/sns/oauth2/access_token?appid={self.appid}&secret={self.secret}&code={code}&grant_type=authorization_code"
        async with self.session.get(api) as res:
            # {"code": code, "state": state}
            return await res.json(content_type=None)

    async def get_user_info(self, access_token, openid):
        """获取用户信息"""
        api = f"https://api.weixin.qq.com/sns/userinfo?access_token={access_token}&openid={openid}&lang=zh_CN"
        async with self.session.get(api) as res:
            # {"code": code, "state": state}
            return await res.json(content_type=None)
