import os
import time
import requests
from telegram.ext import Updater, CommandHandler
from apscheduler.schedulers.background import BackgroundScheduler

# Replace with your Telegram Bot Token
TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')

# Replace with your chat ID
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

# Coinbase API endpoint for BTC price
COINBASE_API_URL = "https://api.coinbase.com/v2/prices/BTC-USD/spot"

last_price = None
last_notification_time = 0

def get_btc_price():
    response = requests.get(COINBASE_API_URL)
    data = response.json()
    return float(data['data']['amount'])

def send_price_update(context):
    global last_price
    current_price = get_btc_price()
    
    if last_price is None:
        last_price = current_price
    
    message = f"Current BTC Price: ${current_price:.2f}"
    context.bot.send_message(chat_id=CHAT_ID, text=message)
    
    check_price_change(context, current_price)

def check_price_change(context, current_price):
    global last_price, last_notification_time
    
    if last_price is not None:
        price_change = abs(current_price - last_price) / last_price
        
        if price_change >= 0.02 and time.time() - last_notification_time >= 300:  # 5 minutes cooldown
            change_percentage = price_change * 100
            direction = "increased" if current_price > last_price else "decreased"
            message = f"Alert: BTC price has {direction} by {change_percentage:.2f}%\nCurrent price: ${current_price:.2f}"
            context.bot.send_message(chat_id=CHAT_ID, text=message)
            last_notification_time = time.time()
    
    last_price = current_price

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Bot started. You will receive hourly BTC price updates. Use /price to get the current price.")

def get_price(update, context):
    current_price = get_btc_price()
    message = f"Current BTC Price: ${current_price:.2f}"
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("price", get_price))

    scheduler = BackgroundScheduler()
    scheduler.add_job(send_price_update, 'interval', hours=1, args=[updater])
    scheduler.start()

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()