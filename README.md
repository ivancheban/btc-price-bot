# BTC Price Update Bot

This Telegram bot provides real-time updates on Bitcoin (BTC) price changes. It fetches the current BTC price from the Binance API and sends notifications to a specified Telegram chat when significant price changes occur.

## Features

- Fetches real-time BTC price from Binance API.
- Sends price updates to a specified Telegram chat.
- Notifies on price changes of 2% or more.
- Sends hourly updates even if the price change is less than 2%.
- Responds to manual price check commands.

## Requirements

- Python 3.7+
- `python-telegram-bot` library
- `pytz` library
- `apscheduler` library
- `aiohttp` library

## Installation

1. Clone this repository
2. Install the required packages:
    ```python
    pip install python-telegram-bot pytz apscheduler aiohttp
    ```
3. Set up your Telegram bot and obtain the API token
4. Set the `TOKEN` environment variable with your Telegram bot token

## Configuration

- `CHAT_ID`: The ID of the Telegram chat where updates will be sent
- `KYIV_TZ`: The timezone used for timestamps (default: 'Europe/Kyiv')

## Usage

1. Run the script:
    ```python
    python btc_price_bot.py
    ```
2. The bot will start polling for updates and checking the BTC price every 10 seconds
3. Use the `/price` command in the Telegram chat to manually request the current BTC price

## How it works

- The bot fetches the BTC price from the Binance API every 10 seconds
- If the price has changed by 2% or more since the last update, a notification is sent
- If an hour has passed since the last update, a notification is sent regardless of the price change
- The bot uses emojis to indicate price movement:
- 🟩 for price increase
- 🔻 for price decrease
- ▪️ for no change (rare with float values)

## Error Handling

- The bot logs errors when failing to fetch the BTC price
- If the API request fails, it will be logged with the status code

## Contributing

Contributions, issues, and feature requests are welcome. Feel free to check [issues page](https://github.com/yourusername/btc-price-update-bot/issues) if you want to contribute.

## License

[MIT](https://choosealicense.com/licenses/mit/)