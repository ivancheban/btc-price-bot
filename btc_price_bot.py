import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from datetime import datetime, timedelta
import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import aiohttp

# Enable detailed logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv('TOKEN')
KYIV_TZ = pytz.timezone('Europe/Kyiv')
CHAT_ID = '-456143424'

last_btc_price = None
last_notification_time = None

async def get_btc_price():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd') as response:
                if response.status == 200:
                    data = await response.json()
                    return data['bitcoin']['usd']
                else:
                    logger.error(f"API request failed with status code: {response.status}")
                    return None
    except Exception as e:
        logger.error(f"Error fetching BTC price: {str(e)}")
        return None

async def send_btc_price_update(context: ContextTypes.DEFAULT_TYPE, price: float, force: bool = False, chat_id: str = CHAT_ID):
    global last_btc_price, last_notification_time
    current_time = datetime.now(KYIV_TZ)

    if last_btc_price is None:
        last_btc_price = price
        last_notification_time = current_time
        await context.bot.send_message(chat_id=chat_id, text=f"🚨 BTC Price Update 🚨\nCurrent BTC price: ${price:,.2f}")
        return

    price_change_percent = abs(price - last_btc_price) / last_btc_price * 100

    if force or price_change_percent >= 2 or (current_time - last_notification_time) >= timedelta(hours=1):
        emoji = "🟢" if price > last_btc_price else "🔻"
        message = f"🚨 BTC Price Update 🚨\nCurrent BTC price: ${price:,.2f}\n{emoji} Change: {price_change_percent:.2f}%"
        await context.bot.send_message(chat_id=chat_id, text=message)
        last_btc_price = price
        last_notification_time = current_time

async def check_btc_price(context: ContextTypes.DEFAULT_TYPE):
    price = await get_btc_price()
    if price:
        await send_btc_price_update(context, price)
    else:
        logger.error("Failed to fetch BTC price")

async def price_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    price = await get_btc_price()
    if price:
        await send_btc_price_update(context, price, force=True, chat_id=update.effective_chat.id)
    else:
        await update.message.reply_text("Sorry, I couldn't fetch the BTC price at the moment.")

def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("price", price_command))

    scheduler = AsyncIOScheduler()
    scheduler.add_job(check_btc_price, 'interval', minutes=5, args=[application])
    scheduler.start()

    application.run_polling()

if __name__ == '__main__':
    main()