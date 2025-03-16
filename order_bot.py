from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters, ConversationHandler
import logging
from datetime import datetime
import json
import os
from dotenv import load_dotenv
import telegram

# Загружаем переменные окружения
load_dotenv()

# Настраиваем логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Состояния разговора
MENU, MEAT_TYPE, FLAVOR, WEIGHT, CART, DELIVERY_CHOICE, DELIVERY_INFO, ORDERING = range(8)

# Категории товаров и их позиции
PRODUCTS = {
    "Курка": {
        "BBQ": {
            "50г": {"price": 110, "description": "Ніжне куряче філе зі смаком барбекю"},
            "100г": {"price": 210, "description": "Ніжне куряче філе зі смаком барбекю"},
            "250г": {"price": 500, "description": "Ніжне куряче філе зі смаком барбекю"}
        },
        "З перцем": {
            "50г": {"price": 110, "description": "Гострі снеки з курки з чорним перцем"},
            "100г": {"price": 210, "description": "Гострі снеки з курки з чорним перцем"},
            "250г": {"price": 500, "description": "Гострі снеки з курки з чорним перцем"}
        },
        "Пармезан": {
            "50г": {"price": 110, "description": "Снеки з курки з ароматним пармезаном"},
            "100г": {"price": 210, "description": "Снеки з курки з ароматним пармезаном"},
            "250г": {"price": 500, "description": "Снеки з курки з ароматним пармезаном"}
        },
        "З грибами": {
            "50г": {"price": 110, "description": "Снеки з курки з грибним смаком"},
            "100г": {"price": 210, "description": "Снеки з курки з грибним смаком"},
            "250г": {"price": 500, "description": "Снеки з курки з грибним смаком"}
        },
        "Сметана-зелень": {
            "50г": {"price": 110, "description": "Снеки з курки зі смаком сметани та зелені"},
            "100г": {"price": 210, "description": "Снеки з курки зі смаком сметани та зелені"},
            "250г": {"price": 500, "description": "Снеки з курки зі смаком сметани та зелені"}
        }
    },
    "Свинина": {
        "З перцем": {
            "50г": {"price": 150, "description": "Гострі снеки зі свинини з чорним перцем"},
            "100г": {"price": 300, "description": "Гострі снеки зі свинини з чорним перцем"},
            "250г": {"price": 600, "description": "Гострі снеки зі свинини з чорним перцем"}
        },
        "З сиром": {
            "50г": {"price": 150, "description": "Снеки зі свинини з сирним смаком"},
            "100г": {"price": 300, "description": "Снеки зі свинини з сирним смаком"},
            "250г": {"price": 600, "description": "Снеки зі свинини з сирним смаком"}
        },
        "З томатом": {
            "50г": {"price": 150, "description": "Снеки зі свинини зі смаком томатів"},
            "100г": {"price": 300, "description": "Снеки зі свинини зі смаком томатів"},
            "250г": {"price": 600, "description": "Снеки зі свинини зі смаком томатів"}
        }
    }
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Початок роботи з ботом"""
    # Ініціалізуємо кошик користувача
    if 'cart' not in context.user_data:
        context.user_data['cart'] = {}
    
    keyboard = [
        [InlineKeyboardButton("🥨 Меню", callback_data='menu')],
        [InlineKeyboardButton("🛒 Кошик", callback_data='cart')],
        [InlineKeyboardButton("❓ Допомога", callback_data='help')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = ("👋 Ласкаво просимо до нашого бота снеків!\n\n"
                   "🚚 Доставка:\n"
                   "- По Києву безкоштовно при замовленні від 3000₴\n"
                   "- Відправка Новою Поштою по всій Україні\n\n"
                   "Оберіть дію:")

    try:
        if update.callback_query:
            query = update.callback_query
            await query.answer()
            if query.message:
                await query.message.edit_text(text=welcome_text, reply_markup=reply_markup)
            else:
                await query.message.reply_text(text=welcome_text, reply_markup=reply_markup)
        elif update.message:
            await update.message.reply_text(text=welcome_text, reply_markup=reply_markup)
        return MENU
    except Exception as e:
        logger.error(f"Error in start handler: {e}")
        # Если произошла ошибка, пытаемся отправить новое сообщение
        if update.effective_chat:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=welcome_text,
                reply_markup=reply_markup
            )
        return MENU

async def show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показує меню з видами м'яса"""
    try:
        query = update.callback_query
        await query.answer()
        
        keyboard = [
            [InlineKeyboardButton("🍗 Курка", callback_data='meat_Курка')],
            [InlineKeyboardButton("🥓 Свинина", callback_data='meat_Свинина')],
            [InlineKeyboardButton("🔙 Назад", callback_data='back_to_start')]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if query.message:
            await query.message.edit_text(
                text="Оберіть вид м'яса:",
                reply_markup=reply_markup
            )
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Оберіть вид м'яса:",
                reply_markup=reply_markup
            )
        return MEAT_TYPE
    except Exception as e:
        logger.error(f"Error in show_menu: {e}")
        return await start(update, context)

async def show_flavors(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показує смаки для обраного виду м'яса"""
    try:
        query = update.callback_query
        await query.answer()
        
        meat_type = query.data.split('_')[1]
        context.user_data['selected_meat'] = meat_type
        
        # Словник емодзі для кожного смаку
        flavor_emojis = {
            "BBQ": "🔥",
            "З перцем": "🌶️",
            "Пармезан": "🧀",
            "З грибами": "🍄",
            "Сметана-зелень": "🌿",
            "З сиром": "🧀",
            "З томатом": "🍅"
        }
        
        keyboard = []
        for flavor in PRODUCTS[meat_type].keys():
            emoji = flavor_emojis.get(flavor, "")
            keyboard.append([InlineKeyboardButton(f"{emoji} {flavor}", callback_data=f'flavor_{flavor}')])
        
        if context.user_data.get('cart'):
            keyboard.append([InlineKeyboardButton("✅ Оформити замовлення", callback_data='checkout')])
        
        keyboard.append([InlineKeyboardButton("🛒 Кошик", callback_data='cart')])
        keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data='menu')])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if query.message:
            await query.message.edit_text(
                text=f"Оберіть смак для {meat_type}:",
                reply_markup=reply_markup
            )
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"Оберіть смак для {meat_type}:",
                reply_markup=reply_markup
            )
        return FLAVOR
    except Exception as e:
        logger.error(f"Error in show_flavors: {e}")
        return await start(update, context)

async def show_weights(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показує доступні ваги для обраного смаку"""
    query = update.callback_query
    await query.answer()
    
    flavor = query.data.split('_')[1]
    meat_type = context.user_data['selected_meat']
    context.user_data['selected_flavor'] = flavor
    
    keyboard = []
    for weight, details in PRODUCTS[meat_type][flavor].items():
        keyboard.append([
            InlineKeyboardButton(
                f"{weight} - {details['price']}₴",
                callback_data=f'weight_{weight}'
            )
        ])
    
    # Добавляем кнопку оформления заказа, если в корзине есть товары
    if context.user_data.get('cart'):
        keyboard.append([InlineKeyboardButton("✅ Оформити замовлення", callback_data='checkout')])
    
    keyboard.append([InlineKeyboardButton("🛒 Кошик", callback_data='cart')])
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data=f'meat_{meat_type}')])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text=f"Оберіть вагу для {meat_type} {flavor}:\n\n{PRODUCTS[meat_type][flavor]['50г']['description']}",
        reply_markup=reply_markup
    )
    return WEIGHT

async def add_to_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Додає товар до кошика"""
    query = update.callback_query
    await query.answer()
    
    weight = query.data.split('_')[1]
    meat_type = context.user_data['selected_meat']
    flavor = context.user_data['selected_flavor']
    
    product_name = f"{meat_type} {flavor} {weight}"
    product_key = f"{meat_type}_{flavor}_{weight}"
    
    if 'cart' not in context.user_data:
        context.user_data['cart'] = {}
    
    if product_key in context.user_data['cart']:
        context.user_data['cart'][product_key]['quantity'] += 1
    else:
        context.user_data['cart'][product_key] = {
            'name': product_name,
            'price': PRODUCTS[meat_type][flavor][weight]['price'],
            'quantity': 1
        }
    
    # Возвращаемся к выбору категории мяса
    keyboard = [
        [InlineKeyboardButton("🍗 Курка", callback_data='meat_Курка')],
        [InlineKeyboardButton("🥓 Свинина", callback_data='meat_Свинина')],
        [InlineKeyboardButton("✅ Оформити замовлення", callback_data='checkout')],
        [InlineKeyboardButton("🛒 Кошик", callback_data='cart')],
        [InlineKeyboardButton("🔙 Назад", callback_data='back_to_start')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=f"✅ {product_name} додано до кошика!\n\n"
             f"Оберіть вид м'яса для продовження покупок:",
        reply_markup=reply_markup
    )
    return MEAT_TYPE

async def show_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показує вміст кошика"""
    query = update.callback_query
    await query.answer()
    
    if not context.user_data.get('cart'):
        keyboard = [[InlineKeyboardButton("🔙 До меню", callback_data='menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text="Ваш кошик порожній!",
            reply_markup=reply_markup
        )
        return MENU
    
    cart_text = "🛒 Ваш кошик:\n\n"
    total = 0
    
    for item_key, item_data in context.user_data['cart'].items():
        subtotal = item_data['price'] * item_data['quantity']
        total += subtotal
        cart_text += f"{item_data['name']} x{item_data['quantity']} = {subtotal}₴\n"
    
    cart_text += f"\nРазом: {total}₴"
    
    keyboard = [
        [InlineKeyboardButton("✅ Оформити замовлення", callback_data='checkout')],
        [InlineKeyboardButton("🗑 Очистити кошик", callback_data='clear_cart')],
        [InlineKeyboardButton("🔙 Повернутися до меню", callback_data='menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=cart_text,
        reply_markup=reply_markup
    )
    return CART

async def clear_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Очищує кошик"""
    query = update.callback_query
    await query.answer()
    
    context.user_data['cart'] = {}
    
    keyboard = [[InlineKeyboardButton("🔙 До меню", callback_data='menu')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text="Кошик очищено!",
        reply_markup=reply_markup
    )
    return MENU

async def calculate_total(cart):
    """Підраховує загальну суму замовлення"""
    total = 0
    for item_data in cart.values():
        total += item_data['price'] * item_data['quantity']
    return total

async def checkout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Починає процес оформлення замовлення"""
    query = update.callback_query
    await query.answer()
    
    # Формируем текст с содержимым корзины
    cart_text = "🛒 Ваше замовлення:\n\n"
    total = 0
    
    for item_key, item_data in context.user_data['cart'].items():
        subtotal = item_data['price'] * item_data['quantity']
        total += subtotal
        cart_text += f"• {item_data['name']} x{item_data['quantity']} = {subtotal}₴\n"
    
    cart_text += f"\nРазом: {total}₴\n\n"
    
    # Добавляем информацию о бесплатной доставке по Киеву
    if total >= 3000:
        cart_text += "🎉 Вам доступна безкоштовна доставка по Києву!\n\n"
    
    cart_text += "Оберіть спосіб доставки:"
    
    # Всегда показываем оба варианта доставки
    delivery_options = [
        [InlineKeyboardButton("📦 Нова Пошта", callback_data='delivery_nova_poshta')],
        [InlineKeyboardButton("🚚 Доставка по Києву", callback_data='delivery_kyiv')],
        [InlineKeyboardButton("🔙 Назад", callback_data='cart')]
    ]
    
    reply_markup = InlineKeyboardMarkup(delivery_options)
    
    await query.edit_message_text(
        text=cart_text,
        reply_markup=reply_markup
    )
    return DELIVERY_CHOICE

async def process_delivery_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обробляє вибір способу доставки"""
    query = update.callback_query
    await query.answer()
    
    delivery_type = query.data.split('_')[1]
    context.user_data['delivery_type'] = delivery_type
    
    if delivery_type == 'nova_poshta':
        message = (
            "📦 Доставка Новою Поштою\n\n"
            "Будь ласка, надішліть всю інформацію в такому форматі:\n\n"
            "1. Ім'я\n"
            "2. Прізвище\n"
            "3. Телефон\n"
            "4. Місто\n"
            "5. Номер відділення\n\n"
            "Наприклад:\n"
            "Іван\n"
            "Петренко\n"
            "+380991234567\n"
            "Київ\n"
            "12"
        )
    else:
        message = (
            "🚚 Доставка по Києву\n\n"
            "Будь ласка, надішліть всю інформацію в такому форматі:\n\n"
            "1. Ім'я\n"
            "2. Прізвище\n"
            "3. Телефон\n"
            "4. Вулиця\n"
            "5. Номер будинку\n"
            "6. Номер квартири (якщо є)\n\n"
            "Наприклад:\n"
            "Іван\n"
            "Петренко\n"
            "+380991234567\n"
            "Хрещатик\n"
            "1\n"
            "123"
        )
    
    keyboard = [[InlineKeyboardButton("🔙 Назад до кошика", callback_data='cart')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text=message, reply_markup=reply_markup)
    return DELIVERY_INFO

async def process_delivery_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обробляє інформацію про доставку"""
    delivery_info = update.message.text.strip()
    delivery_type = context.user_data.get('delivery_type')
    
    # Разбиваем информацию на строки
    info_lines = [line.strip() for line in delivery_info.split('\n') if line.strip()]
    
    try:
        if delivery_type == 'nova_poshta':
            if len(info_lines) < 5:
                await update.message.reply_text(
                    "❌ Для доставки Новою Поштою потрібна наступна інформація:\n"
                    "1. Ім'я\n"
                    "2. Прізвище\n"
                    "3. Телефон\n"
                    "4. Місто\n"
                    "5. Номер відділення\n\n"
                    "Будь ласка, надішліть всю інформацію одним повідомленням"
                )
                return DELIVERY_INFO
                
            info_dict = {
                'Ім\'я': info_lines[0],
                'Прізвище': info_lines[1],
                'Телефон': info_lines[2],
                'Місто': info_lines[3],
                'Відділення': info_lines[4]
            }
        else:  # delivery_kyiv
            if len(info_lines) < 5:
                await update.message.reply_text(
                    "❌ Для доставки по Києву потрібна наступна інформація:\n"
                    "1. Ім'я\n"
                    "2. Прізвище\n"
                    "3. Телефон\n"
                    "4. Вулиця\n"
                    "5. Номер будинку\n"
                    "6. Номер квартири (якщо є)\n\n"
                    "Будь ласка, надішліть всю інформацію одним повідомленням"
                )
                return DELIVERY_INFO
                
            info_dict = {
                'Ім\'я': info_lines[0],
                'Прізвище': info_lines[1],
                'Телефон': info_lines[2],
                'Вулиця': info_lines[3],
                'Будинок': info_lines[4]
            }
            if len(info_lines) > 5:
                info_dict['Квартира'] = info_lines[5]
        
        # Формуємо замовлення
        order = {
            'user_id': update.effective_user.id,
            'username': update.effective_user.username,
            'delivery_type': 'Нова Пошта' if delivery_type == 'nova_poshta' else 'Доставка по Києву',
            'delivery_info': info_dict,
            'items': context.user_data['cart'],
            'total': await calculate_total(context.user_data['cart']),
            'timestamp': datetime.now().isoformat(),
            'status': 'new'
        }
        
        # Зберігаємо замовлення
        save_order(order)
        
        # Формуємо повідомлення для адміністратора
        admin_message = (
            "🛍 Нове замовлення!\n\n"
            f"Спосіб доставки: {order['delivery_type']}\n\n"
            "Інформація про доставку:\n"
        )
        
        for key, value in info_dict.items():
            admin_message += f"{key}: {value}\n"
        
        admin_message += "\nЗамовлені товари:\n"
        
        for item_data in order['items'].values():
            subtotal = item_data['price'] * item_data['quantity']
            admin_message += f"- {item_data['name']} x{item_data['quantity']} = {subtotal}₴\n"
        
        admin_message += f"\nЗагальна сума: {order['total']}₴"
        
        # Надсилаємо повідомлення адміністратору
        admin_id = os.getenv('ADMIN_ID')
        if admin_id:
            try:
                await context.bot.send_message(chat_id=admin_id, text=admin_message)
            except Exception as e:
                logger.error(f"Помилка при відправці повідомлення адміністратору: {e}")
        
        # Очищуємо кошик
        context.user_data['cart'] = {}
        
        # Відправляємо підтвердження користувачу
        keyboard = [[InlineKeyboardButton("🔙 До головного меню", callback_data='start')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "✅ Дякуємо за замовлення! Ми зв'яжемося з вами найближчим часом для підтвердження.",
            reply_markup=reply_markup
        )
        return MENU
        
    except Exception as e:
        logger.error(f"Помилка при обробці інформації про доставку: {e}")
        await update.message.reply_text(
            "❌ Виникла помилка при обробці інформації. Будь ласка, перевірте формат введених даних і спробуйте ще раз."
        )
        return DELIVERY_INFO

def save_order(order):
    """Сохраняет заказ в файл (временное решение)"""
    filename = 'orders.json'
    orders = []
    
    # Читаем существующие заказы
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            orders = json.load(f)
    
    # Добавляем новый заказ
    orders.append(order)
    
    # Сохраняем обновленный список заказов
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(orders, f, ensure_ascii=False, indent=4)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показує довідку з використання бота"""
    query = update.callback_query
    await query.answer()
    
    help_text = """
🤖 Як користуватися ботом:

1. Натисніть кнопку "Меню" для перегляду доступних категорій
2. Оберіть категорію та товар
3. Додайте товари до кошика
4. Перейдіть до кошика для оформлення замовлення
5. Слідуйте інструкціям для завершення замовлення

Якщо у вас виникли проблеми, напишіть нам: @support
    """
    
    keyboard = [[InlineKeyboardButton("🔙 До головного меню", callback_data='start')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=help_text,
        reply_markup=reply_markup
    )
    return MENU

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик ошибок"""
    logger.error(f"Update {update} caused error {context.error}")
    
    error_message = "Виникла помилка при обробці вашого запиту. Будь ласка, спробуйте ще раз або напишіть /start"
    
    try:
        if update and update.effective_message:
            if isinstance(context.error, telegram.error.BadRequest):
                if "Message is not modified" in str(context.error):
                    # Игнорируем ошибку о неизмененном сообщении
                    return
                elif "Button_data_invalid" in str(context.error):
                    # Отправляем новое сообщение с корректными кнопками
                    await start(update, context)
                    return
            
            # Для других ошибок отправляем сообщение об ошибке
            await update.effective_message.reply_text(error_message)
    except Exception as e:
        logger.error(f"Error in error handler: {e}")
        # Если все попытки обработать ошибку не удались, пытаемся отправить новое сообщение
        if update and update.effective_chat:
            try:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=error_message
                )
            except Exception as e:
                logger.error(f"Failed to send error message: {e}")

def main():
    """Запуск бота"""
    token = os.getenv('BOT_TOKEN')
    if not token:
        logger.error("Не знайдено токен бота! Переконайтеся, що він вказаний у файлі .env")
        return
    
    application = Application.builder().token(token).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            MENU: [
                CallbackQueryHandler(show_menu, pattern='^menu$'),
                CallbackQueryHandler(show_cart, pattern='^cart$'),
                CallbackQueryHandler(help_command, pattern='^help$'),
                CallbackQueryHandler(start, pattern='^start$'),
                CallbackQueryHandler(checkout, pattern='^checkout$')
            ],
            MEAT_TYPE: [
                CallbackQueryHandler(show_flavors, pattern='^meat_'),
                CallbackQueryHandler(start, pattern='^back_to_start$'),
                CallbackQueryHandler(show_cart, pattern='^cart$'),
                CallbackQueryHandler(checkout, pattern='^checkout$')
            ],
            FLAVOR: [
                CallbackQueryHandler(show_weights, pattern='^flavor_'),
                CallbackQueryHandler(show_menu, pattern='^menu$'),
                CallbackQueryHandler(show_cart, pattern='^cart$'),
                CallbackQueryHandler(checkout, pattern='^checkout$')
            ],
            WEIGHT: [
                CallbackQueryHandler(add_to_cart, pattern='^weight_'),
                CallbackQueryHandler(show_flavors, pattern='^meat_'),
                CallbackQueryHandler(show_cart, pattern='^cart$'),
                CallbackQueryHandler(checkout, pattern='^checkout$')
            ],
            CART: [
                CallbackQueryHandler(checkout, pattern='^checkout$'),
                CallbackQueryHandler(clear_cart, pattern='^clear_cart$'),
                CallbackQueryHandler(show_menu, pattern='^menu$')
            ],
            DELIVERY_CHOICE: [
                CallbackQueryHandler(process_delivery_choice, pattern='^delivery_'),
                CallbackQueryHandler(show_cart, pattern='^cart$')
            ],
            DELIVERY_INFO: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, process_delivery_info)
            ]
        },
        fallbacks=[CommandHandler('start', start)]
    )
    
    application.add_handler(conv_handler)
    
    # Добавляем обработчик ошибок
    application.add_error_handler(error_handler)
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main() 