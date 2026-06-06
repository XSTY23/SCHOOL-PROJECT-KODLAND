import logging
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from config import BOT_TOKEN
from database import init_db, seed_initial_data, add_student, get_schedule_for_day, get_all_schedule
from messages import format_schedule, format_weekly_schedule, EASTER_EGG, get_random_motivation

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

init_db()
seed_initial_data()

def get_day_key(offset=0):
    days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    target_date = datetime.now() + timedelta(days=offset)
    return days[target_date.weekday()]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    add_student(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name or ''
    )
    
    keyboard = [
        [InlineKeyboardButton("📖 Расписание на сегодня", callback_data="today")],
        [InlineKeyboardButton("📅 Расписание на завтра", callback_data="tomorrow")],
        [InlineKeyboardButton("🗓️ Всё расписание на неделю", callback_data="week")],
        [InlineKeyboardButton("🎓 О школе", callback_data="about")],
        [InlineKeyboardButton("📊 Моя статистика", callback_data="stats")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    

    current_hour = datetime.now().hour
    if 8 <= current_hour < 12:
        time_greeting = "Доброе утро! ☀️"
    elif 12 <= current_hour < 18:
        time_greeting = "Добрый день! 🌤️"
    else:
        time_greeting = "Добрый вечер! 🌙"
    
    welcome_text = (
        f"✨ *{time_greeting}, {user.first_name}!* ✨\n\n"
        "Добро пожаловать в бот нашей онлайн-школы! 🎓\n\n"
        "Я помогу тебе всегда быть в курсе расписания занятий.\n"
        "Просто выбери нужную кнопку ниже 👇\n\n"
        f"_{get_random_motivation()}_"
    )
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

# Обработчик нажатий на кнопки
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    
    if query.data == "today":
        day_key = get_day_key(0)
        lessons = get_schedule_for_day(day_key)
        response = format_schedule(day_key, lessons)
        
    elif query.data == "tomorrow":
        day_key = get_day_key(1)
        lessons = get_schedule_for_day(day_key)
        response = format_schedule(day_key, lessons)
        
    elif query.data == "week":
        schedule = get_all_schedule()
        response = format_weekly_schedule(schedule)
        
    elif query.data == "about":
        response = (
            "🎓 О НАШЕЙ ШКОЛЕ\n\n"
             "Мы — современная онлайн-школа программирования.\n\n"
            "✅ Индивидуальный подход\n"
            "✅ Практика с первых уроков\n"
            "✅ Преподаватели-практики\n"
            "✅ Поддержка 24/7\n\n"
            "КОНТАКТЫ:\n"
            "📧 Email: school@example.com\n"
            "💬 Чат: @school_chat\n"
            "🌐 Сайт: school.example.com"
         )
        
    elif query.data == "stats":
        response = (
            f"📊 *Статистика для {user.first_name}*\n\n"
            "Ты активно пользуешься ботом! 👍\n\n"
            "🏆 Совет: Заглядывай в расписание каждый день,\n"
            "чтобы ничего не пропустить!\n\n"
            f"_{get_random_motivation()}_"
        )
        
    elif query.data == "easter_egg":
        response = EASTER_EGG
    else:
        response = "❌ Ошибка. Попробуй ещё раз."
    
    await query.edit_message_text(
        response,
        parse_mode="Markdown",
        disable_web_page_preview=True
    )

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from database import get_all_schedule  
    response = (
        "📈 *Интересные факты:*\n\n"
        "• В базе данных хранится всё расписание\n"
        "• Каждый студент сохраняется в БД\n"
        "• Мотивационные фразы можно добавлять через SQL\n\n"
        "💡 *Совет разработчику:*\n"
        "Можно расширить статистику, добавив счетчик запросов!"
    )
    await update.message.reply_text(response, parse_mode="Markdown")

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    
    if text == "секрет" or text == "пасхалка":
        await update.message.reply_text(EASTER_EGG, parse_mode="Markdown")
    else:
        await update.message.reply_text(
            "🤔 Используй кнопки, чтобы получить расписание!\n"
            "Напиши /start, чтобы вернуться в меню.",
            parse_mode="Markdown"
        )

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("secret", lambda u, c: u.message.reply_text(EASTER_EGG, parse_mode="Markdown")))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    
    print("🤖 Бот с базой данных SQLite успешно запущен!")
    print("📁 Файл БД: school.db")
    print("💡 Для просмотра БД используй: sqlite3 school.db")
    app.run_polling()

if __name__ == '__main__':
    main()
