import random
from telegram import Bot, Update, ParseMode
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackContext, Updater
import re
from datetime import datetime, timedelta

# Чаты из сети
allowed_chats = [-1002243020675, -1002231043599, -1002230509696]
# Чат для репортов
report_chat_id = -1002230509696

# Инициализация бота
bot_token = "7513028997:AAHE_E0SkCt43GrMUQeOin96wR61m92oyHk"
bot = Bot(token=bot_token)

# Словарь для хранения жалоб
reports = {}

def is_chat_allowed(chat_id):
    """Проверяет, находится ли чат в разрешённой сети."""
    return chat_id in allowed_chats

def is_admin(chat_id, user_id, context):
    """Проверяет, является ли пользователь администратором."""
    admins = context.bot.get_chat_administrators(chat_id)
    return any(admin.user.id == user_id for admin in admins)

def escape_markdown(text):
    """Экранирует специальные символы для MarkdownV2."""
    escape_chars = r'\*_\[\]()~>#+-=|{}.!'
    return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', text)

def handle_report(update: Update, context: CallbackContext):
    """Обрабатывает команду репорта."""
    message = update.message
    chat_id = message.chat.id

    # Проверка, что бот находится в нужной сети чатов
    if not is_chat_allowed(chat_id):
        update.message.reply_text("Я создан для сетки чатов Nazarchikooo тут я буду как риба в песке 🐠")
        return

    # Проверка на ответное сообщение
    if not message.reply_to_message:
        update.message.reply_text("Внимание что бы использовать репорты нужно использовать команду в ответ на сообщения нарушителя 😉")
        return

    reported_user = message.reply_to_message.from_user
    reporting_user = message.from_user.id

    # Проверка, если жалоба на администратора
    if is_admin(chat_id, reported_user.id, context):
        update.message.reply_text(random.choice([
            "iq видимо тебе не хватает 😁",
            "Та ты бестрашный!",
            "эм ты хоть понимаешь что на админа кидать жалобу нельзя??"
        ]))
        return

    # Проверка, если жалоба на себя
    if reported_user.id == reporting_user:
        update.message.reply_text(random.choice([
            "iq видимо тебе не хватает 😁",
            "Та ты бестрашный!",
            "эм ты хоть понимаешь что на самого себя кидать жалобу нельзя??"
        ]))
        return

    # Обновляем количество жалоб на пользователя
    current_time = datetime.now()
    if reported_user.id not in reports:
        reports[reported_user.id] = []

    # Добавляем текущую жалобу
    reports[reported_user.id].append(current_time)

    # Удаляем жалобы старше 10 минут
    reports[reported_user.id] = [time for time in reports[reported_user.id] if time > current_time - timedelta(minutes=10)]

    # Проверяем, превышает ли количество жалоб 5
    if len(reports[reported_user.id]) > 5:
        # Кикаем пользователя
        context.bot.kick_chat_member(chat_id, reported_user.id)
        update.message.reply_text("Пользователь был исключен черезмерное жалование на него 😎")
        # Очищаем записи о жалобах
        del reports[reported_user.id]
        return

    # Отправка сообщения о репорте в чат модерации
    send_report_to_chat(message.from_user, reported_user, message.reply_to_message, chat_id)
    update.message.reply_text("✅Жалоба на это сообщение отправлена! Спасибо что помогаете отлавливать нарушителей")

def send_report_to_chat(reporting_user, reported_user, reported_message, chat_id):
    """Отправляет репорт в специальный чат модерации с корректными ссылками и экранированием MarkdownV2."""
    message_id = reported_message.message_id
    chat_id_cleaned = str(chat_id).replace("-100", "")  # Убираем префикс "-100" для супергрупп
    message_link = f"https://t.me/c/{chat_id_cleaned}/{message_id}"

    # Экранирование специальных символов в тексте
    reporting_user_name = escape_markdown(reporting_user.username or "Пользователь")
    reported_user_name = escape_markdown(reported_user.username or "Пользователь")
    reported_message_text = escape_markdown(reported_message.text or "стикер/гифка/фото")

    # Создание текста с использованием MarkdownV2 для форматирования
    report_text = (
        f"Поступила новая жалоба\n"
        f"Жалоба была отправлена человеком [{reporting_user_name}](tg://user?id={reporting_user.id})\n"
        f"На кого поступила жалоба [{reported_user_name}](tg://user?id={reported_user.id})\n"
        f"Сообщение: {reported_message_text}\n"
        f"[Перейти к сообщению]({message_link})"
    )

    # Отправка сообщения с включённым MarkdownV2
    bot.send_message(chat_id=report_chat_id, text=report_text, parse_mode=ParseMode.MARKDOWN_V2)

def handle_rules(update: Update, context: CallbackContext):
    """Отправляет правила чата."""
    rules_text = (
        "Правила сетки чатов Nazarchikooo\n"
        "Что бы мы могли культурно и вежливо общаться, вы должны соблюдать правила, которые найдете ниже:\n"
        "[Изучить правила](https://teletype.in/@nazarchikooo/jE_1XiMradb)"
    )
    update.message.reply_text(rules_text, parse_mode=ParseMode.MARKDOWN_V2)

def main():
    """Основная функция для запуска бота."""
    updater = Updater(token=bot_token, use_context=True)
    dispatcher = updater.dispatcher

    # Хэндлер для команды репорта
    report_handler = MessageHandler(Filters.text & Filters.regex(r'(\.репорт|!репорт|/report)'), handle_report)
    dispatcher.add_handler(report_handler)

    # Хэндлер для команды правил
    rules_handler = MessageHandler(Filters.text & Filters.regex(r'(правила|Правила|/rules)'), handle_rules)
    dispatcher.add_handler(rules_handler)

    # Запуск бота
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
