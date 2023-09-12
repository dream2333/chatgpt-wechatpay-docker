import tomllib

with open("secerts.toml", "rb") as f:
    secrets = tomllib.load(f)

# 后端配置
JWT_SECRET = secrets["server"]["key"]

# 数据库配置
DB_URL = secrets["server"]["db"]
TORTOISE_ORM = {
    "connections": {"default": DB_URL},
    "apps": {
        "models": {
            "models": ["app.models", "aerich.models"],
            "default_connection": "default",
        },
    },
}

# OPENAI配置
OPENAI_KEYS = secrets["openai"]["key"]
OPENAI_PROXY = ""

# 微信公众号配置
WECHAT_APPID = secrets["wechat"]["appid"]
WECHAT_APPSECRET = secrets["wechat"]["app_secret"]
# 微信支付商户号，服务商模式下为服务商户号，即官方文档中的sp_mchid。
MCHID = secrets["wechat_pay"]["mchid"]

# 商户证书私钥，此文件不要放置在下面设置的CERT_DIR目录里。
with open(secrets["wechat_pay"]["cert_key"]) as f:
    PRIVATE_KEY = f.read()

# 商户证书序列号
CERT_SERIAL_NO = secrets["wechat_pay"]["serial_no"]

# API v3密钥， https://pay.weixin.qq.com/wiki/doc/apiv3/wechatpay/wechatpay3_2.shtml
APIV3_KEY = secrets["wechat_pay"]["apiv3_key"]

# APPID，应用ID，服务商模式下为服务商应用ID，即官方文档中的sp_appid，也可以在调用接口的时候覆盖。
APPID = secrets["wechat_pay"]["appid"]

# 回调地址，也可以在调用接口的时候覆盖。
NOTIFY_URL = secrets["wechat_pay"]["notify_url"]

# 微信支付平台证书缓存目录，初始调试的时候可以设为None，首次使用确保此目录为空目录。
CERT_DIR = "./cert"

# 接入模式：False=直连商户模式，True=服务商模式。
PARTNER_MODE = False

# 代理设置，None或者{"https": "http://10.10.1.10:1080"}，详细格式参见[https://requests.readthedocs.io/en/latest/user/advanced/#proxies](https://requests.readthedocs.io/en/latest/user/advanced/#proxies)
PROXY = None
