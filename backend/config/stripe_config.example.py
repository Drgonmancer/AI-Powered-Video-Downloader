import os

# 复制为 stripe_config.py 或设置环境变量（推荐）
STRIPE_CONFIG = {
    "secret_key": os.getenv("STRIPE_SECRET_KEY", "sk_test_你的密钥"),
    "publishable_key": os.getenv("STRIPE_PUBLISHABLE_KEY", "pk_test_你的密钥"),
    "webhook_secret": os.getenv("STRIPE_WEBHOOK_SECRET", "whsec_你的webhook密钥"),
    "prices": {
        "basic": {
            "price_id": os.getenv("STRIPE_PRICE_BASIC", "price_你的基础版价格ID"),
            "amount": 1990,
            "currency": "cny",
            "name": "基础版会员",
        },
        "pro": {
            "price_id": os.getenv("STRIPE_PRICE_PRO", "price_你的专业版价格ID"),
            "amount": 7990,
            "currency": "cny",
            "name": "专业版会员",
        },
    },
    "success_url": os.getenv("STRIPE_SUCCESS_URL", "http://127.0.0.1:9000/payment/success"),
    "cancel_url": os.getenv("STRIPE_CANCEL_URL", "http://127.0.0.1:9000/pricing"),
}


def get_stripe_config():
    return STRIPE_CONFIG
