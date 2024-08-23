import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from datetime import datetime, timedelta
import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import aiohttp

# Enable detailed logging
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv('TOKEN')
KYIV_TZ = pytz.timezone('Europe/Kyiv')

# ... (keep all your existing functions)

async def get_btc_price():
    async with aiohttp.ClientSession() as session:
        async with session.get('https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd') as response:
            if response.status == 200:
                data = await response.json()
                return data['bitcoin']['usd']
            else:
                return None

async def price_command(update: Update, context: CallbackContext) -> None:
    price = await get_btc_price()
    if price:
        await update.message.reply_text(f"Current BTC price: ${price:,.2f}")
    else:
        await update.message.reply_text("Sorry, I couldn't fetch the BTC price at the moment.")

async def daily_btc_notification(context: CallbackContext, chat_id: str) -> None:
    try:
        logger.info("Executing scheduled BTC job...")
        price = await get_btc_price()
        if price:
            message = f"🚨 Daily BTC Update 🚨\nCurrent BTC price: ${price:,.2f}"
            response = await context.bot.send_message(chat_id=chat_id, text=message)
            logger.info(f"BTC message sent with message id {response.message_id}")
        else:
            logger.error("Failed to fetch BTC price")
    except Exception as e:
        logger.error(f"Failed to send BTC message: {str(e)}")

def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("when_salary", when_salary))
    application.add_handler(CommandHandler("price", price_command))  # Add this line

    scheduler = AsyncIOScheduler()
    scheduler.add_job(daily_salary_notification, 'cron', hour=10, minute=30, args=[application, '-1001581609986'], timezone=KYIV_TZ)
    scheduler.add_job(daily_btc_notification, 'cron', hour=12, minute=0, args=[application, '-1001581609986'], timezone=KYIV_TZ)
    scheduler.start()

    application.run_polling()

if __name__ == '__main__':
    main()