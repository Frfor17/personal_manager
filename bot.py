# bot.py
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import config
from main import app
import asyncio

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Привет! Я бот с AI-агентом. Задай мне вопрос!')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Просто напиши вопрос, а я передам его AI-агенту!')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    try:
        # Передаем только user_input, остальные поля инициализируются в main.py
        result = await asyncio.get_event_loop().run_in_executor(
            None,
            app.invoke,
            {
                "user_input": user_message,
                # Убираем llm_response, так как его больше нет в состоянии
            }
        )
        
        # Теперь используем final_response вместо llm_response
        bot_response = result["final_response"]
        if not bot_response or bot_response.isspace():
            bot_response = "Не удалось получить осмысленный ответ от AI. Попробуйте переформулировать вопрос."
        
        await update.message.reply_text(bot_response)
        
    except Exception as e:
        print(f"Ошибка в боте: {e}")
        await update.message.reply_text("Произошла внутренняя ошибка. Попробуйте еще раз.")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Ошибка Telegram: {context.error}")

def main():
    app_bot = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()
    
    app_bot.add_handler(CommandHandler("start", start_command))
    app_bot.add_handler(CommandHandler("help", help_command))
    app_bot.add_handler(MessageHandler(filters.TEXT, handle_message))
    app_bot.add_error_handler(error_handler)
    
    print("Бот запущен и использует AI-агента...")
    app_bot.run_polling(poll_interval=3)

if __name__ == "__main__":
    main()