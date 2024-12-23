import asyncio
import aiohttp
import telebot
from telebot import types
from io import BytesIO
import time
import logging
from functools import wraps
import json
import base64
import random
from datetime import datetime, timedelta
import threading
import re

BOT_TOKEN = "8085178802:AAH95w-wJxOSXmheHgaL-yLMB1U7V8biQs4"
IMGBB_API_KEY = "5444a4ac2da619fbd8cdbe21cc57e6ff"
TEXT_API_URL = "http://aeza.theksenon.pro/v1/api/text/generate"
IMAGE_API_URL = "http://aeza.theksenon.pro/v1/api/image/generate"
IMGBB_API_URL = "https://api.imgbb.com/1/upload"
ADMIN_ID = 7410579418
ADMIN2_ID = 1345626274

API_KEYS = [
    "ksenon-191e5f78345721e3",
    "ksenon-9f1e7fd32627ebb6",
    "ksenon-39c730b332fc2a42",
    "ksenon-93665cfce67d67ec",
    "ksenon-5b2c779e6a05362b",
    "ksenon-5aab37eb303021be",
    "ksenon-61707e4a24cc55c5",
    "ksenon-fbb78676bbca89b6",
    "ksenon-f95b9899a6cbe336",
    "ksenon-3f482cc3c0e68fe3",
    "ksenon-33a22f56a6c3e769",
    "ksenon-259dd3f0a30dd4de",
    "ksenon-b35e4fde1576c91b",
    "ksenon-8fafd75c42936307",
    "ksenon-44fa38b084c3a942",
    "ksenon-768dee8916896da9",
    "ksenon-0fc7b293f097a9c1",
    "ksenon-d327833700c2a542",
    "ksenon-c808bb776460cc13",
    "ksenon-4be8a1a9abfaeb6a",
    "ksenon-e76096f4621f87c8",
    "ksenon-7fd8a1e396e31084",
    "ksenon-1038f169fb90dbcc",
    "ksenon-70b990fa29906895",
    "ksenon-54f17562c5e45827",
    "ksenon-1652458f85a612d6",
    "ksenon-3d5a8e301f2e3fe7",
    "ksenon-a9c850f91532bad6"
]

MODELS = {
    "text": {
        "GPT-4": "gpt-4o",
        "GPT-3.5": "gpt-3.5-turbo",
        "Claude 3.5": "claude-3-5-sonnet",
        "Llama-3.2-90B-Vision-Instruct": "meta-llama/Llama-3.2-90B-Vision-Instruct",
        "Llama-3.2-11B-Vision-Instruct": "meta-llama/Llama-3.2-11B-Vision-Instruct",
        "Llama-3.2-1B-Instruct": "meta-llama/Llama-3.2-1B-Instruct",
        "Llama-3.1-70B": "meta-llama/Llama-3.1-70B-Instruct",
        "Mistral-7B-Instruct-V0.3": "mistralai/Mistral-7B-Instruct-v0.3",
        "Mistral-7B-Instruct-V0.2": "mistralai/Mistral-7B-Instruct-v0.2",
        "Mistral-Large": "mistral-large",
        "Mixtral-8x22B-Instruct-v0.1": "mistralai/Mixtral-8x22B-Instruct-v0.1",
        "Gemini-1.5-Pro": "gemini-1.5-pro",
        "Gemini-1.5-Flash": "gemini-1.5-flash",
        "Command-R-Plus-08-2024": "CohereForAI/c4ai-command-r-plus-08-2024",
        "Command-R-08-2024": "command-r-08-2024",
        "Command-R-Plus": "command-r-plus",
        "Qwen2.5-72B-Instruct": "Qwen/Qwen2.5-72B-Instruct",
        "Qwen2-72B-Instruct": "Qwen/Qwen2-72B-Instruct",
        "OpenAI": "openai",
        "OpenAI/Whisper-Large": "openai/whisper-large-v3",
        "Meta-Llama-3.1-70B-Instruct": "meta-llama/Meta-Llama-3.1-70B-Instruct",
        "Meta-Llama-3.1-8B-Instruct-Turbo": "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
        "Google/Gemma-7B": "google/gemma-7b-it-lora",
        "Google/Gemma-1.1-7B-IT": "google/gemma-1.1-7b-it",
        "HuggingFace-Starchat2-15b-v0.1": "HuggingFaceH4/starchat2-15b-v0.1",
        "HuggingFace-Zephyr-7B-Alpha": "HuggingFaceH4/zephyr-7b-alpha",
        "Llama-2-13B-Chat": "meta-llama/Llama-2-13b-chat-hf",
        "Llama-2-7B-Chat": "meta-llama/Llama-2-7b-chat-hf",
        "Microsoft/Phi-3-medium-4k-instruct": "microsoft/Phi-3-medium-4k-instruct",
        "Microsoft/DialoGPT-medium": "microsoft/DialoGPT-medium",
        "Cohere/Command-R": "command",
        "Cohere/Command-R-08-2024": "command-r-08-2024",
        "BlackBoxAI": "blackboxai",
        "BlackBoxAI-Pro": "blackboxai-pro",
        "Yi-1.5-34B-Chat": "01-ai/Yi-1.5-34B-Chat",
        "Yi-34B-Chat": "01-ai/Yi-34B-Chat",
        "PythonAgent": "PythonAgent",
        "JavaAgent": "JavaAgent",
        "FastAPIAgent": "FastAPIAgent",
        "FirebaseAgent": "FirebaseAgent"
    },
    "image": {
        "🎨 FLUX PRO MG": "flux-pro-mg",
        "🔧 FLUX DEV": "flux-dev",
        "🚀 SD3 ULTRA": "sd3-ultra",
        "✨ PIXART ALPHA": "pixart-alpha"
    }
}

class AccessError(Exception):
    pass

class PremiumManager:
    def __init__(self):
        self.premium_file = "prem.json"
        self.premium_users = self.load_premium_users()
        threading.Thread(target=self.check_premium_expiration, daemon=True).start()

    def load_premium_users(self):
        try:
            with open(self.premium_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save_premium_users(self):
        with open(self.premium_file, 'w') as f:
            json.dump(self.premium_users, f)

    def parse_duration(self, duration_str):
        if duration_str == "inf":
            return "inf"
            
        pattern = r'^(\d+)([mhdwy])$'
        match = re.match(pattern, duration_str)
        
        if not match:
            raise ValueError("Invalid duration format")
            
        amount = int(match.group(1))
        unit = match.group(2)
        
        if unit == 'm' and amount > 0:  # minutes
            return timedelta(minutes=amount)
        elif unit == 'h' and amount > 0:  # hours
            return timedelta(hours=amount)
        elif unit == 'd' and amount > 0:  # days
            return timedelta(days=amount)
        elif unit == 'w' and amount > 0:  # weeks
            return timedelta(weeks=amount)
        elif unit == 'y' and amount > 0 and amount <= 1:  # years (max 1 year)
            return timedelta(days=365 * amount)
        else:
            raise ValueError("Invalid duration value")

    def add_premium(self, user_id, duration_str):
        user_id = str(user_id)
        now = datetime.now()
        
        try:
            duration = self.parse_duration(duration_str)
            
            if duration == "inf":
                expiry = "inf"
            else:
                expiry = (now + duration).timestamp()
            
            self.premium_users[user_id] = {
                "expiry": expiry,
                "added_at": now.timestamp()
            }
            self.save_premium_users()
            return True, None
            
        except ValueError as e:
            return False, str(e)

    def remove_premium(self, user_id):
        user_id = str(user_id)
        if user_id in self.premium_users:
            del self.premium_users[user_id]
            self.save_premium_users()
            return True
        return False

    def is_premium(self, user_id):
        user_id = str(user_id)
        if user_id not in self.premium_users:
            return False
            
        expiry = self.premium_users[user_id]["expiry"]
        if expiry == "inf":
            return True
            
        return float(expiry) > datetime.now().timestamp()

    def check_premium_expiration(self):
        while True:
            now = datetime.now().timestamp()
            expired_users = []
            
            for user_id, data in self.premium_users.items():
                if data["expiry"] != "inf" and float(data["expiry"]) < now:
                    expired_users.append(user_id)
            
            for user_id in expired_users:
                self.remove_premium(user_id)
            
            time.sleep(5)

    def get_duration_text(self, duration_str):
        if duration_str == "inf":
            return "навсегда"
            
        pattern = r'^(\d+)([mhdwy])$'
        match = re.match(pattern, duration_str)
        
        if not match:
            return "неизвестный период"
            
        amount = int(match.group(1))
        unit = match.group(2)
        
        unit_text = {
            'm': ['минуту', 'минуты', 'минут'],
            'h': ['час', 'часа', 'часов'],
            'd': ['день', 'дня', 'дней'],
            'w': ['неделю', 'недели', 'недель'],
            'y': ['год', 'года', 'лет']
        }[unit]
        
        if amount % 10 == 1 and amount != 11:
            return f"{amount} {unit_text[0]}"
        elif 2 <= amount % 10 <= 4 and (amount < 10 or amount > 20):
            return f"{amount} {unit_text[1]}"
        else:
            return f"{amount} {unit_text[2]}"

premium_manager = PremiumManager()

def get_random_api_key():
    return random.choice(API_KEYS)

def check_access(user_id):
    if user_id == ADMIN_ID or user_id == ADMIN2_ID or premium_manager.is_premium(user_id):
        return True
    raise AccessError("Access Denied")

def admin_access_required(func):
    @wraps(func)
    def wrapper(message, *args, **kwargs):
        try:
            check_access(message.from_user.id)
            return func(message, *args, **kwargs)
        except AccessError:
            bot.reply_to(
                message,
                "<b>⛔️ ДОСТУП ЗАКРЫТ</b>\n<b>Этот бот только для премиум пользователей!</b>",
                parse_mode="HTML"
            )
    return wrapper

def admin_only(func):
    @wraps(func)
    def wrapper(message, *args, **kwargs):
        if message.from_user.id != ADMIN_ID and message.from_user.id != ADMIN2_ID:
            bot.reply_to(
                message,
                "<b>⛔️ Эта команда доступна только администратору!</b>",
                parse_mode="HTML"
            )
            return
        return func(message, *args, **kwargs)
    return wrapper


bot = telebot.TeleBot(BOT_TOKEN)
user_states = {}

@bot.message_handler(commands=['start'])
@admin_access_required
def start(message):
    user_id = message.from_user.id
    user_states[user_id] = {"state": "main_menu"}
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    text_btn = types.InlineKeyboardButton("📝 ГЕНЕРАЦИЯ ТЕКСТА", callback_data="mode_text")
    image_btn = types.InlineKeyboardButton("🎨 ГЕНЕРАЦИЯ КАРТИНОК", callback_data="mode_image")
    markup.add(text_btn, image_btn)
    
    bot.send_message(
        message.chat.id,
        f"<b>👋 ДОБРО ПОЖАЛОВАТЬ!</b>\n\n"
        "<b>ВЫБЕРИТЕ РЕЖИМ РАБОТЫ:</b>",
        reply_markup=markup,
        parse_mode="HTML"
    )

@bot.message_handler(commands=['addprem'])
@admin_only
def add_premium_handler(message):
    try:
        _, user_id, duration = message.text.split()
        user_id = int(user_id)
        
        success, error = premium_manager.add_premium(user_id, duration)
        
        if success:
            duration_text = premium_manager.get_duration_text(duration)
            bot.reply_to(
                message,
                f"<b>✅ Премиум успешно выдан пользователю {user_id} на {duration_text}</b>",
                parse_mode="HTML"
            )
            # Notify the other admin
            other_admin = ADMIN2_ID if message.from_user.id == ADMIN_ID else ADMIN_ID
            bot.send_message(
                other_admin,
                f"<b>ℹ️ Администратор {message.from_user.id} выдал премиум пользователю {user_id} на {duration_text}</b>",
                parse_mode="HTML"
            )
        else:
            bot.reply_to(
                message,
                f"<b>❌ Ошибка: {error}</b>\n\n"
                "<b>Формат команды:</b>\n"
                "<code>/addprem [id] [длительность]</code>\n\n"
                "<b>Доступные форматы длительности:</b>\n"
                "• <code>Nm</code> - минуты (например: 30m)\n"
                "• <code>Nh</code> - часы (например: 12h)\n"
                "• <code>Nd</code> - дни (например: 30d)\n"
                "• <code>Nw</code> - недели (например: 2w)\n"
                "• <code>1y</code> - год\n"
                "• <code>inf</code> - навсегда",
                parse_mode="HTML"
            )
    except ValueError:
        bot.reply_to(
            message,
            "<b>❌ Неверный формат команды!</b>\n\n"
            "<b>Используйте:</b> <code>/addprem [id] [длительность]</code>\n\n"
            "<b>Примеры:</b>\n"
            "• <code>/addprem 123456789 30m</code> - 30 минут\n"
            "• <code>/addprem 123456789 12h</code> - 12 часов\n"
            "• <code>/addprem 123456789 7d</code> - 7 дней\n"
            "• <code>/addprem 123456789 2w</code> - 2 недели\n"
            "• <code>/addprem 123456789 1y</code> - 1 год\n"
            "• <code>/addprem 123456789 inf</code> - навсегда",
            parse_mode="HTML"
        )

@bot.message_handler(commands=['remprem'])
@admin_only
def remove_premium_handler(message):
    try:
        _, user_id = message.text.split()
        user_id = int(user_id)
        
        if premium_manager.remove_premium(user_id):
            bot.reply_to(
                message,
                f"<b>✅ Премиум успешно удален у пользователя {user_id}</b>",
                parse_mode="HTML"
            )
            # Notify the other admin
            other_admin = ADMIN2_ID if message.from_user.id == ADMIN_ID else ADMIN_ID
            bot.send_message(
                other_admin,
                f"<b>ℹ️ Администратор {message.from_user.id} удалил премиум у пользователя {user_id}</b>",
                parse_mode="HTML"
            )
        else:
            bot.reply_to(
                message,
                f"<b>❌ У пользователя {user_id} нет премиума</b>",
                parse_mode="HTML"
            )
    except ValueError:
        bot.reply_to(
            message,
            "<b>❌ Неверный формат команды!</b>\n"
            "<b>Используйте:</b> <code>/remprem [id]</code>",
            parse_mode="HTML"
        )

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    try:
        check_access(call.from_user.id)
        user_id = call.from_user.id
        
        if call.data.startswith("mode_"):
            mode = call.data.split("_")[1]
            user_states[user_id] = {"state": f"selecting_{mode}_model"}
            
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            for model_name in MODELS[mode].keys():
                markup.add(types.KeyboardButton(model_name))
            
            bot.send_message(
                call.message.chat.id,
                "<b>📝 ВЫБЕРИТЕ МОДЕЛЬ:</b>",
                reply_markup=markup,
                parse_mode="HTML"
            )
            
        elif call.data.startswith("regenerate_"):
            model = call.data.split("_")[1]
            if call.message.reply_to_message:
                asyncio.run(generate_image(call.message.reply_to_message, model))
        
        bot.answer_callback_query(call.id)
        
    except AccessError:
        bot.answer_callback_query(call.id, "⛔️ Доступ запрещён", show_alert=True)

@bot.message_handler(content_types=['text'])
@admin_access_required
def handle_text(message):
    user_id = message.from_user.id
    user_state = user_states.get(user_id, {}).get("state", "main_menu")
    
    if user_state == "selecting_text_model":
        if message.text in MODELS["text"]:
            model = MODELS["text"][message.text]
            user_states[user_id] = {
                "state": "texting",
                "model": model,
                "model_name": message.text
            }
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(types.KeyboardButton("🔄 СМЕНИТЬ РЕЖИМ"))
            bot.reply_to(
                message,
                f"<b>✅ МОДЕЛЬ ВЫБРАНА: {message.text}</b>\n<b>💬 Отправьте текст запроса</b>",
                reply_markup=markup,
                parse_mode="HTML"
            )
            
    elif user_state == "selecting_image_model":
        if message.text in MODELS["image"]:
            model = MODELS["image"][message.text]
            user_states[user_id] = {
                "state": "drawing",
                "model": model,
                "model_name": message.text
            }
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(types.KeyboardButton("🔄 СМЕНИТЬ РЕЖИМ"))
            bot.reply_to(
                message,
                f"<b>✅ МОДЕЛЬ ВЫБРАНА: {message.text}</b>\n<b>🎨 Опишите картинку</b>",
                reply_markup=markup,
                parse_mode="HTML"
            )
            
    elif user_state in ["texting", "drawing"]:
        if message.text == "🔄 СМЕНИТЬ РЕЖИМ":
            start(message)
            return
            
        if user_state == "texting":
            asyncio.run(generate_text(message))
        else:
            asyncio.run(generate_image(message))

async def generate_text(message):
    user_id = message.from_user.id
    user_state = user_states.get(user_id, {})
    model = user_state.get("model")
    model_name = user_state.get("model_name")
    
    if not model:
        bot.reply_to(message, "<b>❌ Сначала выберите модель!</b>", parse_mode="HTML")
        return
        
    bot.send_chat_action(message.chat.id, 'typing')
    
    try:
        response = await api_request(TEXT_API_URL, {
            "model": model,
            "prompt": message.text
        })
        
        if "error" in response:
            bot.reply_to(
                message,
                f"<b>❌ ОШИБКА:</b> <b>{response['error']}</b>",
                parse_mode="HTML"
            )
            return
            
        text = response.get("response", "Нет ответа")
        response_text = (
            f"<b>{text}</b>\n\n"
            f"<b>🤖 МОДЕЛЬ:</b> <b>{model_name}</b>"
        )
        
        if len(response_text) > 4096:
            with open("response.txt", "w", encoding="utf-8") as file:
                file.write(text)
            with open("response.txt", "rb") as file:
                bot.send_document(
                    message.chat.id,
                    file,
                    caption=f"<b>🤖 МОДЕЛЬ: {model_name}</b>",
                    parse_mode="HTML"
                )
        else:
            bot.reply_to(message, response_text, parse_mode="HTML")
            
    except Exception as e:
        bot.reply_to(
            message,
            f"<b>❌ ОШИБКА:</b> <b>{str(e)}</b>",
            parse_mode="HTML"
        )

async def generate_image(message):
    user_id = message.from_user.id
    user_state = user_states.get(user_id, {})
    model = user_state.get("model")
    model_name = user_state.get("model_name")
    
    if not model:
        bot.reply_to(message, "<b>❌ Сначала выберите модель!</b>", parse_mode="HTML")
        return
        
    try:
        progress_msg = bot.reply_to(
            message,
            "<b>🎨 ГЕНЕРАЦИЯ ИЗОБРАЖЕНИЯ...</b>",
            parse_mode="HTML"
        )
        
        response = await api_request(IMAGE_API_URL, {
            "model": model,
            "prompt": message.text
        })
        
        if "error" in response:
            bot.edit_message_text(
                f"<b>❌ ОШИБКА:</b> <b>{response['error']}</b>",
                chat_id=message.chat.id,
                message_id=progress_msg.message_id,
                parse_mode="HTML"
            )
            return
            
        image_url = response.get("url")
        if not image_url:
            bot.edit_message_text(
                "<b>❌ ОШИБКА: Не получен URL изображения</b>",
                chat_id=message.chat.id,
                message_id=progress_msg.message_id,
                parse_mode="HTML"
            )
            return
            
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as img_response:
                if img_response.status == 200:
                    image_data = BytesIO(await img_response.read())
                    image_data.name = "image.png"
                    
                    try:
                        imgbb_url = await upload_to_imgbb(image_data)
                        image_data.seek(0)
                        
                        markup = types.InlineKeyboardMarkup()
                        markup.add(
                            types.InlineKeyboardButton(
                                "🔄 СГЕНЕРИРОВАТЬ ЗАНОВО",
                                callback_data=f"regenerate_{model}"
                            )
                        )
                        
                        bot.delete_message(
                            chat_id=message.chat.id,
                            message_id=progress_msg.message_id
                        )
                        
                        caption = (
                            f"<b>🎨 МОДЕЛЬ: [{model_name}]</b>\n"
                            f"<b>🌐 ЗАПРОС: {message.text}</b>\n\n"
                            f"<b>{imgbb_url}</b>"
                        )
                        
                        bot.send_photo(
                            message.chat.id,
                            image_data,
                            caption=caption,
                            reply_markup=markup,
                            parse_mode="HTML"
                        )
                    except Exception as e:
                        bot.edit_message_text(
                            f"<b>❌ ОШИБКА загрузки на ImgBB:</b> <b>{str(e)}</b>",
                            chat_id=message.chat.id,
                            message_id=progress_msg.message_id,
                            parse_mode="HTML"
                        )
                else:
                    bot.edit_message_text(
                        "<b>❌ ОШИБКА: Не удалось загрузить изображение</b>",
                        chat_id=message.chat.id,
                        message_id=progress_msg.message_id,
                        parse_mode="HTML"
                    )
                    
    except Exception as e:
        try:
            bot.edit_message_text(
                f"<b>❌ ОШИБКА:</b> <b>{str(e)}</b>",
                chat_id=message.chat.id,
                message_id=progress_msg.message_id,
                parse_mode="HTML"
            )
        except:
            bot.reply_to(
                message,
                f"<b>❌ ОШИБКА:</b> <b>{str(e)}</b>",
                parse_mode="HTML"
            )

async def upload_to_imgbb(image_data):
    try:
        base64_image = base64.b64encode(image_data.read()).decode('utf-8')
        
        params = {
            'key': IMGBB_API_KEY,
            'image': base64_image
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(IMGBB_API_URL, data=params) as response:
                result = await response.json()
                if result.get('success'):
                    return result['data']['url']
                else:
                    raise Exception("Failed to upload image to ImgBB")
    except Exception as e:
        logging.error(f"ImgBB Upload Error: {e}")
        raise

async def api_request(url, data, headers=None):
    api_key = get_random_api_key()
    if headers is None:
        headers = {
            "Authorization": api_key,
            "Content-Type": "application/json"
        }
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, headers=headers, json=data) as response:
                return await response.json()
        except Exception as e:
            logging.error(f"API Error: {e}")
            return {"error": str(e)}

def run_bot():
    while True:
        try:
            logging.info("Bot started...")
            bot.polling(none_stop=True)
        except Exception as e:
            logging.error(f"Bot error: {e}")
            time.sleep(3)

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    run_bot()
