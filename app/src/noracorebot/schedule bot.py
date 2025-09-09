import requests
import pytz
from datetime import datetime, timedelta
from icalendar import Calendar
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# Константы
ICS_URL_TEMPLATE = "https://ruz.spbstu.ru/faculty/123/groups/42153/ical?date={date}"
MOSCOW_TZ = pytz.timezone("Europe/Moscow")

# Запускаем бота
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📅 Эта неделя", callback_data="this_week")],
        [InlineKeyboardButton("📅 Следующая неделя", callback_data="next_week")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выберите неделю:", reply_markup=reply_markup)

# Обработка кнопок
async def handle_week_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    today = datetime.now(MOSCOW_TZ).date()
    if query.data == "this_week":
        start_date = today - timedelta(days=today.weekday())  # Понедельник текущей недели
    else:
        start_date = today - timedelta(days=today.weekday()) + timedelta(days=7)  # Понедельник следующей недели

    await send_schedule(query, start_date)

# Функция получения и отправки расписания
async def send_schedule(query, start_date):
    date_str = start_date.strftime("%Y-%m-%d")
    url = ICS_URL_TEMPLATE.format(date=date_str)
    response = requests.get(url)
    if response.status_code != 200:
        await query.edit_message_text("Не удалось загрузить расписание.")
        return

    cal = Calendar.from_ical(response.content)
    events_by_day = {}

    for component in cal.walk():
        if component.name == "VEVENT":
            start = component.get("DTSTART").dt
            summary = component.get("SUMMARY")
            location = component.get("LOCATION")

            if not isinstance(start, datetime):
                start = datetime.combine(start, datetime.min.time())
            start = start.astimezone(MOSCOW_TZ)

            day_key = start.date()
            if day_key not in events_by_day:
                events_by_day[day_key] = []
            events_by_day[day_key].append(
                (start, f"{start.strftime('%H:%M')} — {summary} ({location})")
            )

    if not events_by_day:
        await query.edit_message_text("На эту неделю занятий нет.")
    else:
        # Сортировка дней и событий
        sorted_days = sorted(events_by_day.keys())
        message_parts = []
        for day in sorted_days:
            events = sorted(events_by_day[day], key=lambda x: x[0])  # сортировка по времени
            day_str = day.strftime("%a, %d.%m.%Y")
            events_text = "\n".join(e[1] for e in events)
            message_parts.append(f"📅 {day_str}\n{events_text}")
        message = "\n\n".join(message_parts)

        await query.edit_message_text(message)

# Основной запуск
def main():
    app = ApplicationBuilder().token("8275475788:AAFjTJjpEZ4DqWey_UB23GFC85VVCIdFWn4").build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_week_choice))

    app.run_polling()

if __name__ == "__main__":
    main()
