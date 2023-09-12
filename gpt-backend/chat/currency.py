import datetime
import requests


def get_key(apikey):
    subscription_url = "https://api.openai.com/v1/dashboard/billing/subscription"
    headers = {"Authorization": "Bearer " + apikey, "Content-Type": "application/json"}
    subscription_response = requests.get(
        subscription_url,
        headers=headers,
        proxies={"https": "http://127.0.0.1:7890"},
    )
    if subscription_response.status_code == 200:
        data = subscription_response.json()
        total = data.get("hard_limit_usd")
    else:
        return subscription_response.text
    # start_date设置为今天日期前99天
    start_date = (datetime.datetime.now() - datetime.timedelta(days=99)).strftime(
        "%Y-%m-%d"
    )
    # end_date设置为今天日期+1
    end_date = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime(
        "%Y-%m-%d"
    )
    billing_url = f"https://api.openai.com/v1/dashboard/billing/usage?start_date={start_date}&end_date={end_date}"
    billing_response = requests.get(
        billing_url, headers=headers, proxies={"https": "http://127.0.0.1:7890"}
    )
    if billing_response.status_code == 200:
        data = billing_response.json()
        total_usage = data.get("total_usage") / 100

    else:
        return billing_response.text

    return (
        f"\n#### 监控key为：{apikey[:-25] + '*' * 25}\n"
        f"#### 总额:\t{total:.2f}  \n"
        f"#### 已用:\t{total_usage:.2f}  \n"
        f"#### 剩余:\t{total - total_usage:.2f}  \n"
    )
