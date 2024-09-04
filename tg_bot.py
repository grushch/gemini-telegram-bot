from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters 
from telegram.constants import ChatAction, ParseMode
from PIL import Image
from io import BytesIO
import asyncio
import os
import logging
import json
from gemini import model, multi_model
from md2tghtml import format_message

PROJECT_DIR = os.path.dirname(__file__)+'/'

logging.basicConfig(format='%(levelname)s - %(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

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
        logging.info("LLM Response: %s", response.text)
        await update.message.reply_text(text=format_message(response.text), parse_mode=ParseMode.HTML, disable_web_page_preview=True)
    except Exception as e:
        logging.exception(e)
    await asyncio.sleep(0.1)

async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.chat.send_action(ChatAction.TYPING)

    images = update.message.photo
    file_list = await asyncio.gather(*[image.get_file() for image in images])
    loaded_images = []
    for file in file_list:
        file_bytes = await file.download_as_bytearray()
        image = Image.open(BytesIO(file_bytes))
        loaded_images.append(image)

    if update.message.caption:
        prompt = update.message.caption
    elif len(loaded_images) > 1:
        prompt = "Analyse and describe this images"
    else:
        prompt = "Analyse and describe this image"

    try:
        response = multi_model.generate_content([prompt, *loaded_images]) # Generate a response by llm
        await update.message.reply_text(text=format_message(response.text), parse_mode=ParseMode.HTML, disable_web_page_preview=True) 
    except Exception as e:
        logging.exception(e)

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.chat.send_action(ChatAction.TYPING)

    voice = update.message.voice
    file = await voice.get_file()
    file_bytes = await file.download_as_bytearray()
    audio_data = {
                    "mime_type": "audio/ogg",
                    "data": bytes(file_bytes)
                    }
    #prompt = 'Can you transcribe this audio'
    prompt = ''

    try:
        response = multi_model.generate_content([prompt, audio_data]) # Generate a response by llm
        logging.info("LLM Response: %s", response.text)
        await update.message.reply_text(
            text=format_message(response.text),
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True
        )
    except Exception as e:
        logging.exception(e)

    await asyncio.sleep(0.1)


if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()

    # Commands
    application.add_handler(CommandHandler('start', start))
    
    # Messages
    application.add_handler(MessageHandler((filters.TEXT), handle_message))

    application.add_handler(MessageHandler((filters.PHOTO), handle_image))

    application.add_handler(MessageHandler((filters.VOICE), handle_voice))


    application.run_polling()
