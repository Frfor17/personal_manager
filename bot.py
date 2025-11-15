# telegram_bot.py
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import config  # твой config.py с токеном

# Функция для команды /start
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Привет! Я простой бот. Просто напиши мне что-нибудь!')

# Функция для команды /help  
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Я просто повторяю твои сообщения! Попробуй написать что-нибудь.')

# Функция для обработки обычных сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    user_name = update.message.chat.first_name
    
    # Просто возвращаем эхо-ответ
    response = f"Привет, {user_name}! Ты написал: '{user_message}'"
    
    await update.message.reply_text(response)

# Функция для обработки ошибок
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Ошибка: {context.error}")

# Главная функция
def main():
    # Создаем приложение с токеном из config.py
    app = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()
    
    # Добавляем обработчики команд
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    
    # Добавляем обработчик текстовых сообщений
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    
    # Добавляем обработчик ошибок
    app.add_error_handler(error_handler)
    
    print("Бот запущен...")
    # Запускаем бота в режиме опроса
    app.run_polling(poll_interval=3)

if __name__ == "__main__":
    main()