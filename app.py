import os
from flask import Flask, request, jsonify
from binance.client import Client
from binance.enums import *
import telebot
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Binance API configuration (use testnet credentials)
BINANCE_API_KEY = os.getenv('BINANCE_API_KEY')
BINANCE_SECRET_KEY = os.getenv('BINANCE_SECRET_KEY')

# Telegram Bot configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# Initialize Binance client
binance_client = Client(BINANCE_API_KEY, BINANCE_SECRET_KEY, testnet=True)

# Initialize Telegram bot
telegram_bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

def send_telegram_message(message):
    try:
        telegram_bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.info(f"Sent Telegram message: {message}")
    except Exception as e:
        logger.error(f"Failed to send Telegram message: {e}")

def execute_binance_order(symbol, side, quantity):
    try:
        order = binance_client.create_order(
            symbol=symbol,
            side=side,
            type=ORDER_TYPE_MARKET,
            quantity=quantity
        )
        logger.info(f"Order executed: {order}")
        return order
    except Exception as e:
        logger.error(f"Failed to execute Binance order: {e}")
        return None

@app.route('/')
def home():
    return "TradingView Webhook Server is running!"

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == 'POST':
        data = request.json
        logger.info(f"Received webhook data: {data}")

        if 'action' not in data or 'symbol' not in data or 'quantity' not in data:
            return jsonify({'status': 'error', 'message': 'Missing required fields'}), 400

        action = data['action']
        symbol = data['symbol']
        quantity = float(data['quantity'])

        if action == 'BUY':
            order = execute_binance_order(symbol, SIDE_BUY, quantity)
            if order:
                send_telegram_message(f"🟢 BUY order executed for {symbol}. Quantity: {quantity}")
        elif action == 'SELL':
            order = execute_binance_order(symbol, SIDE_SELL, quantity)
            if order:
                send_telegram_message(f"🔴 SELL order executed for {symbol}. Quantity: {quantity}")

        elif action == 'TAKE_PROFIT':
            order = execute_binance_order(symbol, SIDE_SELL, quantity)
            if order:
                send_telegram_message(f"💰 TAKE PROFIT order executed for {symbol}. Quantity: {quantity}")
                
        elif action == 'STOP_LOSS':
            order = execute_binance_order(symbol, SIDE_SELL, quantity)
            if order:
                send_telegram_message(f"🛑 STOP LOSS order executed for {symbol}. Quantity: {quantity}")
        else:
            return jsonify({'status': 'error', 'message': 'Invalid action'}), 400

        return jsonify({'status': 'success', 'message': 'Order processed'}), 200
    else:
        return jsonify({'status': 'error', 'message': 'Invalid request method'}), 405

# This condition is true if the script is executed directly
if __name__ == '__main__':
    app.run(debug=False)