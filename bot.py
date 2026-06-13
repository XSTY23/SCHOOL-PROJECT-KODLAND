import logging
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes
from config import BOT_TOKEN
from database import init_db, seed_initial_data, add_student, get_schedule_for_day, get_all_schedule
from messages import format_schedule, format_weekly_schedule, EASTER_EGG, get_random_motivation

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

init_db()
seed_initial_data()

def get_day_key(offset=0):
    days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    target_date = datetime.now() + timedelta(days=offset)
    return days[target_date.weekday()]

# Функция для создания кнопки "В главное меню"
def get_back_button():
    keyboard = [[InlineKeyboardButton("🔙 В главное меню", callback_data="main_menu")]]
    return InlineKeyboardMarkup(keyboard)

# Функция для создания главного меню
def get_main_menu():
    keyboard = [
        [InlineKeyboardButton("📖 Расписание на сегодня", callback_data="today")],
        [InlineKeyboardButton("📅 Расписание на завтра", callback_data="tomorrow")],
        [InlineKeyboardButton("🗓️ Всё расписание на неделю", callback_data="week")],
        [InlineKeyboardButton("🎓 О школе", callback_data="about")],
        [InlineKeyboardButton("📊 Моя статистика", callback_data="stats")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_student(user.id, user.username, user.first_name, user.last_name or '')
    
    current_hour = datetime.now().hour
    if 8 <= current_hour < 12:
        time_greeting = "Доброе утро! ☀️"
    elif 12 <= current_hour < 18:
        time_greeting = "Добрый день! 🌤️"
    else:
        time_greeting = "Добрый вечер! 🌙"
    
    welcome_text = (f"✨ {time_greeting}, {user.first_name}! ✨\n\n"
        "Добро пожаловать в бот нашей онлайн-школы! 🎓\n\n"
        "Я помогу тебе всегда быть в курсе расписания занятий.\n"
        "Просто выбери нужную кнопку ниже 👇\n\n"
        f"{get_random_motivation()}")
    
    await update.message.reply_text(welcome_text, reply_markup=get_main_menu())

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    # Если нажата кнопка "В главное меню"
    if query.data == "main_menu":
        await query.edit_message_text(
            "🔙 *Главное меню*\n\nВыбери нужную опцию:",
            parse_mode="Markdown",
            reply_markup=get_main_menu()
        )
        return
    
    # Обработка остальных кнопок
    if query.data == "today":
        day_key = get_day_key(0)
        lessons = get_schedule_for_day(day_key)
        response = format_schedule(day_key, lessons)
        await query.edit_message_text(
            response,
            parse_mode="Markdown",
            reply_markup=get_back_button()
        )
        
    elif query.data == "tomorrow":
        day_key = get_day_key(1)
        lessons = get_schedule_for_day(day_key)
        response = format_schedule(day_key, lessons)
        await query.edit_message_text(
            response,
            parse_mode="Markdown",
            reply_markup=get_back_button()
        )
        
    elif query.data == "week":
        schedule = get_all_schedule()
        response = format_weekly_schedule(schedule)
        await query.edit_message_text(
            response,
            parse_mode="Markdown",
            reply_markup=get_back_button()
        )
        
    elif query.data == "about":
        response = "🎓 *О НАШЕЙ ШКОЛЕ*\n\nМы - современная онлайн-школа программирования.\n\n✅ Индивидуальный подход\n✅ Практика с первых уроков\n✅ Преподаватели-практики\n✅ Поддержка 24/7"
        await query.edit_message_text(
            response,
            parse_mode="Markdown",
            reply_markup=get_back_button()
        )
        
    elif query.data == "stats":
        response = f"📊 *Статистика*\n\nТы активно пользуешься ботом! 👍\n\n{get_random_motivation()}"
        await query.edit_message_text(
            response,
            parse_mode="Markdown",
            reply_markup=get_back_button()
        )
        
    else:
        await query.edit_message_text("❌ Ошибка", reply_markup=get_back_button())

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    if text == "секрет" or text == "пасхалка":
        await update.message.reply_text(EASTER_EGG)
    else:
        await update.message.reply_text("Используй /start для меню")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(None, message_handler))
    
    print("✅ Бот запущен!")
    app.run_polling()

if __name__ == '__main__':
    main()
