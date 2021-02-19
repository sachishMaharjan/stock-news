import requests
import datetime
from twilio.rest import Client
import os

STOCK = "TSLA"
COMPANY_NAME = "Tesla"
STOCK_API_KEY = os.environ.get("STOCK_API_KEY")
NEWS_API_KEY = os.environ.get("NEWS_API_KEY")
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")

today = datetime.date.today()
today_str = str(datetime.date.today())
yesterday = str(today - datetime.timedelta(days=1))
before_yesterday = str(today - datetime.timedelta(days=2))

## STEP 1: Use https://www.alphavantage.co
stock_parameters = {
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK,
    "apikey": STOCK_API_KEY
}
response = requests.get(url="https://www.alphavantage.co/query", params=stock_parameters)
stock_data = response.json()
stock_price_y = float(stock_data["Time Series (Daily)"][yesterday]["4. close"])
stock_price_by = float(stock_data["Time Series (Daily)"][before_yesterday]["4. close"])

change_percentage = round(((stock_price_y - stock_price_by) / stock_price_by) * 100)
up_down = None

if change_percentage > 0:
    up_down = "🔺"
else:
    up_down = "🔻"


## STEP 2: Use https://newsapi.org
news_parameters = {
    "qInTitle": COMPANY_NAME,
    "from": today_str,
    "language": "en",
    "sortBy": "publishedAt",
    "apiKey": NEWS_API_KEY,
}
news_response = requests.get(url="http://newsapi.org/v2/everything", params=news_parameters)
news_data = news_response.json()
print(news_data)
news_list = news_data["articles"][:3]


## STEP 3: Use https://www.twilio.com
if abs(change_percentage) >= 5:
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

    for news in news_list:
        news_title = news["title"]
        news_description = news["description"]
        print(news_title)
        print(news_description)

        message = client.messages \
            .create(
            body=f"{STOCK}: {up_down}{abs(change_percentage)}%\nHeadline: {news_title}\nBrief: {news_description}",
            from_="+12028755996",
            to="+61405852198",
        )
        print(message.status)

#Optional: Format the SMS message like this: 
"""
TSLA: 🔺2%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
or
"TSLA: 🔻5%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
"""

