import os
import json
import random
import logging
from pathlib import Path
from zoneinfo import ZoneInfo
from datetime import time as dtime, datetime, timedelta

from telegram import (
    Update, InlineKeyboardMarkup, InlineKeyboardButton, ChatMemberUpdated
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, ChatMemberHandler, ContextTypes, filters
)

# ========================= CONFIG =========================
TOKEN = os.getenv("BOT_TOKEN", "7954414982:AAEr72DPiy0DXgCkvfI0xVKvxKcNEw-xlok")

IMG_DIR = "images"
STATE_FILE = "state.json"
ALMATY = ZoneInfo("Asia/Almaty")

DEFAULT_STATE = {
    "CHAT_IDS": [],
    "ADMIN_IDS": [],
    "SEND_HOUR": 12,
    "SEND_MINUTE": 0
}
# ==========================================================

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("bot")


# ---------- Хранилище ----------
def load_state() -> dict:
    if not os.path.exists(STATE_FILE):
        save_state(DEFAULT_STATE)
        return DEFAULT_STATE.copy()
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    for k, v in DEFAULT_STATE.items():
        data.setdefault(k, v)
    data["CHAT_IDS"] = list({int(x) for x in data.get("CHAT_IDS", [])})
    data["ADMIN_IDS"] = list({int(x) for x in data.get("ADMIN_IDS", [])})
    return data

def save_state(state: dict):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

STATE = load_state()


# ---------- Утилиты ----------
def is_admin(user_id: int) -> bool:
    return user_id in STATE["ADMIN_IDS"]

def ensure_images_dir():
    Path(IMG_DIR).mkdir(parents=True, exist_ok=True)

def list_images():
    ensure_images_dir()
    files = [f for f in Path(IMG_DIR).iterdir()
             if f.is_file() and f.suffix.lower() in {".jpg", ".jpeg", ".png", ".gif", ".webp"}]
    files.sort()
    return files

def require_private_and_admin(update: Update) -> tuple[bool, int]:
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    uid = user.id if user else 0

    if chat.type != "private":
        if msg:
            try:
                msg.reply_text("Пиши мне в личку. Управление доступно только админам в ЛС.")
            except Exception:
                pass
        return False, uid

    if not is_admin(uid):
        if msg:
            msg.reply_text("⛔ Нет доступа. Добавь себя в админы командой /setadmin (один раз).")
        return False, uid

    return True, uid

def _compute_next_run(hh: int, mm: int) -> datetime:
    now = datetime.now(ALMATY)
    nxt = now.replace(hour=hh, minute=mm, second=0, microsecond=0)
    if nxt <= now:
        nxt += timedelta(days=1)
    return nxt

def schedule_daily_job(app):
    jq = getattr(app, "job_queue", None)
    if jq is None:
        log.warning('JobQueue недоступен. Установи: pip install "python-telegram-bot[job-queue]==20.7"')
        return

    for job in jq.jobs():
        if job.data == "daily_send":
            job.schedule_removal()

    send_time = dtime(STATE["SEND_HOUR"], STATE["SEND_MINUTE"], tzinfo=ALMATY)
    jq.run_daily(send_random_image_job, time=send_time, data="daily_send")
    log.info(f"Daily job scheduled at {send_time} (Asia/Almaty)")

def admin_panel_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📷 Случайная картинка сейчас", callback_data="send_random_now")],
        [InlineKeyboardButton("📝 Сообщение всем", callback_data="say")],
    ])


# ---------- Рассылка ----------
async def send_to_all_chats_photo(bot, img_path: Path, caption: str | None = None):
    errs = 0
    for chat_id in list(STATE["CHAT_IDS"]):
        try:
            with img_path.open("rb") as fh:
                await bot.send_photo(chat_id, fh, caption=caption)
        except Exception as e:
            errs += 1
            log.warning(f"Не удалось отправить в {chat_id}: {e}")
    return errs

async def send_to_all_chats_photo_by_id(bot, file_id: str, caption: str | None = None):
    errs = 0
    for chat_id in list(STATE["CHAT_IDS"]):
        try:
            await bot.send_photo(chat_id, photo=file_id, caption=caption)
        except Exception as e:
            errs += 1
            log.warning(f"Не удалось отправить фото в {chat_id}: {e}")
    return errs

async def send_to_all_chats_sticker(bot, file_id: str):
    errs = 0
    for chat_id in list(STATE["CHAT_IDS"]):
        try:
            await bot.send_sticker(chat_id, sticker=file_id)
        except Exception as e:
            errs += 1
            log.warning(f"Не удалось отправить стикер в {chat_id}: {e}")
    return errs

async def send_to_all_chats_text(bot, text: str):
    errs = 0
    for chat_id in list(STATE["CHAT_IDS"]):
        try:
            await bot.send_message(chat_id, text)
        except Exception as e:
            errs += 1
            log.warning(f"Не удалось отправить в {chat_id}: {e}")
    return errs

async def send_random_image_job(context: ContextTypes.DEFAULT_TYPE):
    imgs = list_images()
    if not imgs or not STATE["CHAT_IDS"]:
        return
    img = random.choice(imgs)
    # требование: подписывать автопост
    await send_to_all_chats_photo(context.bot, img, caption="Цитата дня:")


# ---------- Команды (только ЛС и только админы) ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ok, _ = require_private_and_admin(update)
    if not ok:
        return
    nxt = _compute_next_run(STATE["SEND_HOUR"], STATE["SEND_MINUTE"])
    await update.message.reply_text(
        "Я живой. Управление — только здесь, в личке с ботом.\n\n"
        "Команды:\n"
        "• /myid — показать твой Telegram ID\n"
        "• /setadmin — добавить СЕБЯ в админы (один раз)\n"
        "• /addadmin <id> — добавить админа по ID\n"
        "• /deladmin <id> — удалить админа\n"
        "• /listadmins — показать админов\n"
        "• /listchats — показать чаты рассылки\n"
        "• /settime HH:MM — время ежедневной рассылки (Asia/Almaty)\n"
        "• /say <текст> — разослать текст сейчас (или пришли фото/стикер после /say)\n"
        "• /panel — панель (картинка сейчас / сообщение всем)\n"
        "• /addimage — загрузить картинку в запас (пришли фото ответом)\n\n"
        f"Следующая автосработка: {nxt.strftime('%Y-%m-%d %H:%M:%S %Z')}"
    )

async def myid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ok, _ = require_private_and_admin(update)
    if not ok:
        return
    await update.message.reply_text(f"Твой ID: {update.effective_user.id}")

async def listchats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ok, _ = require_private_and_admin(update)
    if not ok:
        return
    chats = STATE["CHAT_IDS"]
    if not chats:
        return await update.message.reply_text("Список чатов пуст. Добавь меня в группу — я запомню её.")
    await update.message.reply_text("Чаты для рассылки:\n" + "\n".join(str(i) for i in chats))

async def setadmin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private":
        return
    uid = update.effective_user.id
    if uid not in STATE["ADMIN_IDS"]:
        STATE["ADMIN_IDS"].append(uid)
        save_state(STATE)
        return await update.message.reply_text(f"✅ Добавлен в админы: {uid}")
    await update.message.reply_text("Ты уже админ.")

async def addadmin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ok, _ = require_private_and_admin(update)
    if not ok:
        return
    if not context.args:
        return await update.message.reply_text("Использование: /addadmin <telegram_id>")
    try:
        new_id = int(context.args[0])
    except ValueError:
        return await update.message.reply_text("ID должен быть числом.")
    if new_id not in STATE["ADMIN_IDS"]:
        STATE["ADMIN_IDS"].append(new_id)
        save_state(STATE)
        return await update.message.reply_text(f"✅ Добавлен админ: {new_id}")
    await update.message.reply_text("Этот ID уже в списке админов.")

async def deladmin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ok, _ = require_private_and_admin(update)
    if not ok:
        return
    if not context.args:
        return await update.message.reply_text("Использование: /deladmin <telegram_id>")
    try:
        rem_id = int(context.args[0])
    except ValueError:
        return await update.message.reply_text("ID должен быть числом.")
    if rem_id in STATE["ADMIN_IDS"]:
        STATE["ADMIN_IDS"].remove(rem_id)
        save_state(STATE)
        return await update.message.reply_text(f"🗑️ Удалён админ: {rem_id}")
    await update.message.reply_text("Такого админа нет в списке.")

async def listadmins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ok, _ = require_private_and_admin(update)
    if not ok:
        return
    ids = STATE["ADMIN_IDS"]
    if not ids:
        return await update.message.reply_text("Список админов пуст.")
    await update.message.reply_text("Админы:\n" + "\n".join(str(i) for i in ids))

async def settime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ok, _ = require_private_and_admin(update)
    if not ok:
        return
    if not context.args:
        return await update.message.reply_text("Использование: /settime HH:MM (Asia/Almaty)")
    try:
        hh, mm = context.args[0].split(":")
        hh, mm = int(hh), int(mm)
        if not (0 <= hh <= 23 and 0 <= mm <= 59):
            raise ValueError
    except Exception:
        return await update.message.reply_text("Неверный формат. Пример: /settime 12:30")

    STATE["SEND_HOUR"] = hh
    STATE["SEND_MINUTE"] = mm
    save_state(STATE)

    schedule_daily_job(context.application)
    nxt = _compute_next_run(hh, mm)
    await update.message.reply_text(
        f"✅ Время рассылки обновлено: {hh:02d}:{mm:02d} (Asia/Almaty)\n"
        f"Следующая автосработка: {nxt.strftime('%Y-%m-%d %H:%M:%S %Z')}"
    )

# ---- /say: текст сейчас или вход в режим ожидания медиа/стикера ----
async def say(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ok, _ = require_private_and_admin(update)
    if not ok:
        return
    if context.args:
        text = " ".join(context.args).strip()
        if not text:
            return await update.message.reply_text("Пусто. Пришли текст/фото/стикер после /say.")
        await send_to_all_chats_text(context.bot, text)
        return await update.message.reply_text("✅ Сообщение разослано.")
    await update.message.reply_text(
        "Ок, пришли следующим сообщением **текст**, **фото** или **стикер** для рассылки во все чаты.\nОтмена: /cancel"
    )
    context.user_data["say_mode"] = True

# текст после /say
async def say_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private":
        return
    if not is_admin(update.effective_user.id):
        return
    if not context.user_data.get("say_mode"):
        return
    text = (update.message.text or "").strip()
    if not text:
        return await update.message.reply_text("Пустой текст. Попробуй ещё раз или /cancel.")
    await send_to_all_chats_text(context.bot, text)
    context.user_data["say_mode"] = False
    await update.message.reply_text("✅ Сообщение разослано.")

# фото после /say (без сохранения)
async def say_photo_or_upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # только ЛС и админ
    if update.effective_chat.type != "private":
        return
    if not is_admin(update.effective_user.id):
        return

    # 1) режим загрузки (/addimage) — ПРИОРИТЕТНЕЕ
    if context.user_data.get("await_photo"):
        photo = update.message.photo[-1]
        f = await photo.get_file()
        ensure_images_dir()
        fname = f"{f.file_unique_id}.jpg"
        save_path = Path(IMG_DIR) / fname
        await f.download_to_drive(str(save_path))
        context.user_data["await_photo"] = False
        return await update.message.reply_text(f"✅ Сохранено: {fname}")

    # 2) режим рассылки после /say — без сохранения
    if context.user_data.get("say_mode"):
        file_id = update.message.photo[-1].file_id
        cap = (update.message.caption or "").strip() or None
        await send_to_all_chats_photo_by_id(context.bot, file_id, caption=cap)
        context.user_data["say_mode"] = False
        return await update.message.reply_text("✅ Фото разослано.")

    # иначе игнор


# стикер после /say
async def say_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private":
        return
    if not is_admin(update.effective_user.id):
        return
    if not context.user_data.get("say_mode"):
        return
    file_id = update.message.sticker.file_id
    await send_to_all_chats_sticker(context.bot, file_id)
    context.user_data["say_mode"] = False
    await update.message.reply_text("✅ Стикер разослан.")

# ---------- Панель ----------
async def panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ok, _ = require_private_and_admin(update)
    if not ok:
        return
    await update.message.reply_text("Админ-панель:", reply_markup=admin_panel_kb())

async def on_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    chat = q.message.chat
    uid = q.from_user.id

    if chat.type != "private":
        await q.answer()
        return
    if not is_admin(uid):
        await q.answer("⛔ Нет доступа.", show_alert=True)
        return

    await q.answer()
    if q.data == "send_random_now":
        imgs = list_images()
        if not imgs:
            return await q.edit_message_text("В папке images/ нет картинок.")
        img = random.choice(imgs)
        await send_to_all_chats_photo(context.bot, img, caption="Случайная цитата :0")  # тут без подписи — это ручная отправка
        return await q.edit_message_text("✅ Отправлено во все чаты.", reply_markup=admin_panel_kb())
    if q.data == "say":
        await q.edit_message_text("Пришли текст/фото/стикер. Отмена: /cancel")
        context.user_data["say_mode"] = True


# ---------- Загрузка картинок в запас ----------
async def addimage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ok, _ = require_private_and_admin(update)
    if not ok:
        return
    ensure_images_dir()
    await update.message.reply_text("Пришли фото в ответ на это сообщение. Отмена: /cancel")
    context.user_data["await_photo"] = True

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private":
        return
    if not is_admin(update.effective_user.id):
        return
    context.user_data["await_photo"] = False
    context.user_data["say_mode"] = False
    await update.message.reply_text("Отменено.")


# ---------- Трекинг чатов ----------
def _status_is_member(status: str) -> bool:
    return status in ("member", "administrator", "creator")

async def my_chat_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cmu: ChatMemberUpdated = update.my_chat_member
    chat = cmu.chat
    old = cmu.old_chat_member
    new = cmu.new_chat_member

    if chat.type not in ("group", "supergroup", "channel"):
        return

    was_in = _status_is_member(getattr(old, "status", "left"))
    is_in = _status_is_member(getattr(new, "status", "left"))

    if not was_in and is_in:
        if chat.id not in STATE["CHAT_IDS"]:
            STATE["CHAT_IDS"].append(chat.id)
            save_state(STATE)
            log.info(f"Добавлен новый чат: {chat.id}")
    elif was_in and not is_in:
        if chat.id in STATE["CHAT_IDS"]:
            STATE["CHAT_IDS"].remove(chat.id)
            save_state(STATE)
            log.info(f"Удалён чат: {chat.id}")


# ---------- MAIN ----------
def main():
    if TOKEN == "PASTE_YOUR_BOT_TOKEN_HERE":
        raise SystemExit("Укажи токен в переменной BOT_TOKEN или в коде TOKEN.")

    app = ApplicationBuilder().token(TOKEN).build()

    # Планировщик ежедневной отправки
    schedule_daily_job(app)

    # Команды
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("myid", myid))
    app.add_handler(CommandHandler("setadmin", setadmin))
    app.add_handler(CommandHandler("addadmin", addadmin))
    app.add_handler(CommandHandler("deladmin", deladmin))
    app.add_handler(CommandHandler("listadmins", listadmins))
    app.add_handler(CommandHandler("settime", settime))
    app.add_handler(CommandHandler("listchats", listchats))
    app.add_handler(CommandHandler("say", say))

    # Панель и колбэки
    app.add_handler(CommandHandler("panel", panel))
    app.add_handler(CallbackQueryHandler(on_cb))

    # Режимы после /say и после /addimage
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, say_text))
    app.add_handler(MessageHandler(filters.PHOTO, say_photo_or_upload))
    app.add_handler(MessageHandler(filters.Sticker.ALL, say_sticker))

    # Трекинг, где бот состоит
    app.add_handler(ChatMemberHandler(my_chat_member, chat_member_types=ChatMemberHandler.MY_CHAT_MEMBER))

    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
