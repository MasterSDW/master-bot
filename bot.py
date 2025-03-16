import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import telebot
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Дозволяємо CORS для всіх маршрутів і доменів

# Initialize Telegram bot
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')  # Keep as string

logger.info(f"Bot Token: {BOT_TOKEN}")
logger.info(f"Chat ID: {CHAT_ID}")

bot = telebot.TeleBot(BOT_TOKEN)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit-form', methods=['POST', 'OPTIONS'])
def submit_form():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200

    try:
        logger.info("Received form submission")
        data = request.json
        logger.debug(f"Form data: {data}")
        
        # Validate required fields
        required_fields = ['name', 'phone', 'street', 'building', 'entrance', 'floor', 'apartment', 'problem']
        for field in required_fields:
            if not data.get(field):
                raise ValueError(f"Missing required field: {field}")
        
        # Format message for Telegram
        message = f"""🔔 Нова заявка на ремонт!

👤 Клієнт: {data['name']}
📞 Телефон: {data['phone']}

📍 Адреса:
🏠 Вулиця: {data['street']}
🏢 Будинок: {data['building']}
🚪 Під'їзд: {data['entrance']}
📋 Поверх: {data['floor']}
🔑 Квартира: {data['apartment']}

💬 Опис проблеми:
{data['problem']}"""

        logger.info("Sending message to Telegram")
        try:
            # Send message to Telegram with error handling
            response = bot.send_message(CHAT_ID, message)
            logger.info(f"Message sent successfully: {response}")
        except telebot.apihelper.ApiException as e:
            logger.error(f"Telegram API error: {e}")
            return jsonify({'success': False, 'error': f"Telegram error: {str(e)}"}), 500
        
        return jsonify({'success': True})
    
    except Exception as e:
        logger.error(f"Error processing form: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 