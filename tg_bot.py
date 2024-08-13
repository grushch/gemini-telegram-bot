from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters 
from telegram.constants import ChatAction, ParseMode
import asyncio
import os
import logging
import json
from gemini import model, img_model
from md2tgmd import format_message

PROJECT_DIR = os.path.dirname(__file__)+'/'

logging.basicConfig(format='%(levelname)s - %(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)

with open(PROJECT_DIR+'tokens.gitignore', 'r') as rfile:
    TOKEN = json.load(rfile)['telegram']
    
def new_chat(context: ContextTypes.DEFAULT_TYPE) -> None:
    context.chat_data['chat'] = model.start_chat() # Keep chat session

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    new_chat(context)
    await update.message.reply_text(f'I`am a personal AI assitant bot, ask me something.')


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.chat_data['chat'] is None:
        new_chat(context)
    text = update.message.text
    chat = context.chat_data.get('chat')  # Get the chat session
    await update.message.chat.send_action(ChatAction.TYPING)
    try:
        response =  chat.send_message(text)  # Generate a response by llm
        await update.message.reply_text(text=format_message(response.text), parse_mode=ParseMode.HTML, disable_web_page_preview=True)
    except Exception as e:
        logging.exception(e)
    await asyncio.sleep(0.1)


if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()

    # Commands
    application.add_handler(CommandHandler('start', start))
    
    # Messages
    application.add_handler(MessageHandler((filters.TEXT), handle_message))

    application.run_polling()
