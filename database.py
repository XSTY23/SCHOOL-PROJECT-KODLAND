import sqlite3
from datetime import datetime

DB_NAME = 'school.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS schedule (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            day_of_week TEXT NOT NULL,      -- monday, tuesday, etc.
            time TEXT NOT NULL,              -- 10:00
            subject TEXT NOT NULL,
            teacher TEXT NOT NULL,
            zoom_link TEXT NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS motivation_quotes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quote TEXT NOT NULL,
            is_active BOOLEAN DEFAULT 1
        )
    ''')
    
    conn.commit()
    conn.close()

def add_student(user_id, username, first_name, last_name):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT OR REPLACE INTO students (user_id, username, first_name, last_name, last_active)
        VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
    ''', (user_id, username, first_name, last_name))
    
    conn.commit()
    conn.close()

def get_schedule_for_day(day_key):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT time, subject, teacher, zoom_link 
        FROM schedule 
        WHERE day_of_week = ?
        ORDER BY time
    ''', (day_key,))
    
    lessons = cursor.fetchall()
    conn.close()
     
    return [
        {
            'time': lesson[0],
            'subject': lesson[1],
            'teacher': lesson[2],
            'zoom_link': lesson[3]
        }
        for lesson in lessons
    ]

def get_all_schedule():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    days_order = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    schedule = {}
    
    for day in days_order:
        cursor.execute('''
            SELECT time, subject, teacher, zoom_link 
            FROM schedule 
            WHERE day_of_week = ?
            ORDER BY time
        ''', (day,))
        lessons = cursor.fetchall()
        
        schedule[day] = [
            {
                'time': lesson[0],
                'subject': lesson[1],
                'teacher': lesson[2],
                'zoom_link': lesson[3]
            }
            for lesson in lessons
        ]
    
    conn.close()
    return schedule

def add_lesson(day_of_week, time, subject, teacher, zoom_link):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO schedule (day_of_week, time, subject, teacher, zoom_link)
        VALUES (?, ?, ?, ?, ?)
    ''', (day_of_week, time, subject, teacher, zoom_link))
    
    conn.commit()
    conn.close()

def delete_lesson(lesson_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM schedule WHERE id = ?', (lesson_id,))
    
    conn.commit()
    conn.close()

def get_motivation_quotes():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('SELECT quote FROM motivation_quotes WHERE is_active = 1')
    quotes = cursor.fetchall()
    conn.close()
    
    return [quote[0] for quote in quotes] if quotes else [
        "💪 Учись и развивайся!",
        "🚀 Ты справишься!",
        "🌟 Знания — сила!"
    ]

def add_motivation_quote(quote):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('INSERT INTO motivation_quotes (quote) VALUES (?)', (quote,))
    
    conn.commit()
    conn.close()

# Функция для заполнения начальными данными
def seed_initial_data():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Проверяем, есть ли уже данные
    cursor.execute('SELECT COUNT(*) FROM schedule')
    count = cursor.fetchone()[0]
    
    if count == 0:
        # Начальное расписание
        initial_schedule = [
            ('monday', '10:00', 'Python: Основы', 'Анна', 'https://zoom.us/...'),
            ('monday', '12:00', 'Алгоритмы и структуры данных', 'Максим', 'https://zoom.us/...'),
            ('monday', '15:00', 'Работа над проектом', 'Дмитрий', 'https://zoom.us/...'),
            ('tuesday', '11:00', 'Базы данных SQL', 'Елена', 'https://zoom.us/...'),
            ('tuesday', '14:00', 'Git и командная работа', 'Максим', 'https://zoom.us/...'),
            ('wednesday', '10:00', 'ООП в Python', 'Анна', 'https://zoom.us/...'),
            ('wednesday', '13:00', 'Веб-разработка на Flask', 'Ольга', 'https://zoom.us/...'),
            ('wednesday', '16:00', 'Консультация', 'Дмитрий', 'https://zoom.us/...'),
            ('thursday', '09:00', 'API и интеграции', 'Максим', 'https://zoom.us/...'),
            ('thursday', '12:00', 'Тестирование кода', 'Елена', 'https://zoom.us/...'),
            ('friday', '11:00', 'Финальные проекты', 'Дмитрий', 'https://zoom.us/...'),
            ('friday', '15:00', 'Code Review', 'Анна', 'https://zoom.us/...'),
        ]
        
        cursor.executemany('''
            INSERT INTO schedule (day_of_week, time, subject, teacher, zoom_link)
            VALUES (?, ?, ?, ?, ?)
        ''', initial_schedule)
        
        # Начальные мотивационные фразы
        initial_quotes = [
            "💪 Отличный выбор! Учёба — это инвестиция в будущее!",
            "🚀 Ты уже на шаг ближе к цели!",
            "🌟 Знания — сила. Ты становишься сильнее!",
            "🎯 Сегодня отличный день, чтобы узнать что-то новое!",
            "📚 Помни: даже гении когда-то были новичками!",
            "⚡ Учись, развивайся, достигай!",
            "💡 Каждый урок приближает тебя к мечте!"
        ]
        
        cursor.executemany('INSERT INTO motivation_quotes (quote) VALUES (?)', 
                          [(q,) for q in initial_quotes])
    
    conn.commit()
    conn.close()
