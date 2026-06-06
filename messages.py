import random
from database import get_motivation_quotes

WEEKDAYS_RU = {
    "monday": "ПОНЕДЕЛЬНИК 🌅",
    "tuesday": "ВТОРНИК ⚡",
    "wednesday": "СРЕДА 🔥",
    "thursday": "ЧЕТВЕРГ 🚀",
    "friday": "ПЯТНИЦА 🎉",
    "saturday": "СУББОТА 🌟",
    "sunday": "ВОСКРЕСЕНЬЕ 😴"
}

def get_random_motivation():
    quotes = get_motivation_quotes()
    return random.choice(quotes)

def format_schedule(day_key, lessons):
    if not lessons:
        return f"📭 *{WEEKDAYS_RU[day_key]}*\n✨ Выходной! Отдыхай и набирайся сил ✨"
    
    text = f"📖 *{WEEKDAYS_RU[day_key]}*\n\n"
    for idx, lesson in enumerate(lessons, 1):
        text += f"🔹 *{lesson['time']}* — {lesson['subject']}\n"
        text += f"   👩‍🏫 {lesson['teacher']}\n"
        text += f"   🔗 [Ссылка на занятие]({lesson['zoom_link']})\n\n"
    
    text += f"\n✨ _{get_random_motivation()}_ ✨"
    return text

def format_weekly_schedule(schedule):
    text = "🗓️ *РАСПИСАНИЕ НА НЕДЕЛЮ*\n\n"
    for day_key, lessons in schedule.items():
        if lessons:
            text += f"📌 *{WEEKDAYS_RU[day_key]}*\n"
            for lesson in lessons:
                text += f"   • {lesson['time']} — {lesson['subject']} ({lesson['teacher']})\n"
            text += "\n"
    text += f"\n🌟 {get_random_motivation()}"
    return text

# Easter egg сообщение
EASTER_EGG = "🎁 *Секрет!*\n\nНаши преподаватели каждую пятницу проводят бесплатные консультации с 18:00 до 20:00. Присоединяйся! 🎓"
