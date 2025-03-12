import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

STORY_STEPS = {
    "start": {
        "text": 'доброе утро ! Восколько встанем сегодня ?',
        'options': {
            '1': 'В 7:20',
            '2': 'B 8:10'
        }
    },
    '1': {
        "text": "проснулись поставили уголь и пошли мыть голову, вийдя с душа пошли делать кальян и смотреть новости и не забываем написать Владу <Доброе утро,лубимый>.",
        "options": {
            "3": " выйти в 8:10 на метро",
            "4": " покурить 15 минут и зиказать такси на работу "
        }
    },
    '3': {
        "text": "Выйдя на улицу понять что сегодня самый прекрасный день и с улыбкой ти к метро и улибатся всем прохожым ",
        "options": {
            "5": "зайти на нонстопом",
            "6": "помочь бабушке "
        }
    },
    '5': {
        "text": "Там маленькая очередь и ты понемаешь что есть возможность опоздать ",
        "options": {
            "7": "всеравно купить нонстоп",
            "8": " пойти на работу без нонстопа"
        }
    },
    "6": {
        "text": "Бабушка россипала яблоки и ты регила помочь и вы собераете яблоки по метро с улибкей посколбку иззо тебя другие обди тоже начинают помогать бабушке и тебе все это собрать, бабушка говорит тебе спосибо и говорит < я бы дала тебе яблочко но оно  с пола по этому держи нонстоп солнишко ты очень добрая напаменаешь мою дочку> улибаеться и уходит ",
        "options": {
            "9": 'Бежать на работу ',
            "10": "Идти на работу "
        }
    },
    "9": {
        "text": "Ты опоздала на работу и пришла в 9:05 и видишь корола ",
        "options": {
            "11": "Постаратся обойти чтобы не заметел",
            "12": "Сказать что случилось и пойти работать "
        }
    },
    '2': {
        "text": "Ты попала в меленькую пробку ",
        "options":{
            "9":"123"
        }
    }
}
   
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Початок історії"""
    keyboard = create_keyboard('start')
    await update.message.reply_text(
        "🌟 Ласкаво просимо до інтерактивної історії 'Один день з життя'!\n\n" +
        STORY_STEPS['start']['text'],
        reply_markup=keyboard
    )

def create_keyboard(step_id: str) -> InlineKeyboardMarkup:
    """Створення клавіатури з варіантами вибору"""
    options = STORY_STEPS[step_id]['options']
    keyboard = [
        [InlineKeyboardButton(text, callback_data=key)]
        for key, text in options.items()
    ]
    return InlineKeyboardMarkup(keyboard)

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обробка натискання кнопок"""
    query = update.callback_query
    await query.answer()

    next_step = query.data
    if next_step in STORY_STEPS:
        keyboard = create_keyboard(next_step)
        await query.edit_message_text(
            text=STORY_STEPS[next_step]['text'],
            reply_markup=keyboard
        )
    else:
        await query.edit_message_text(text="🎬 Уволили! Напишіть /start щоб почати спочатку.")

def main() -> None:
    """Запуск бота"""
    # Замените 'YOUR_BOT_TOKEN' на ваш токен от BotFather
    application = Application.builder().token('7747309684:AAFFiCZMZaFUXc7TuDXVjaGyqoxKLrd43-g').build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_click))

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()