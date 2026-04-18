import os
import time
import telebot
from dotenv import load_dotenv
from ppt_generator import generate_pptx

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not BOT_TOKEN:
    print("[XATO] TELEGRAM_BOT_TOKEN topilmadi!")
    exit(1)

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=["start", "help"])
def cmd_start(msg):
    text = (
        "👋 *Salom! Men — Slayd Botman.*\n\n"
        "Barcha dizaynlardan voz kechib oddiy holatga yozildim.\n"
        "Shunchaki **matn** yoki **rasm** yuboring — bot darhol sizga oq fondagi, "
        "o'qishga qulay matn va internetdan tortilgan rasm (DuckDuckGo) bilan "
        "*.pptx* (taqdimot) faylini yuboradi!"
    )
    bot.send_message(msg.chat.id, text, parse_mode="Markdown")


@bot.message_handler(content_types=["photo", "document"])
def handle_photo(msg):
    try:
        if msg.content_type == "photo":
            file_info = bot.get_file(msg.photo[-1].file_id)
        elif msg.document and msg.document.mime_type and msg.document.mime_type.startswith("image/"):
            file_info = bot.get_file(msg.document.file_id)
        else:
            bot.reply_to(msg, "⚠️ Iltimos, faqat *rasm* yoki *matn* yuboring.", parse_mode="Markdown")
            return

        wait_msg = bot.reply_to(msg, "⏳ Rasm qabul qilindi. Yuklab olinmoqda...")
        raw = bot.download_file(file_info.file_path)
        img_name = f"input_{msg.chat.id}_{int(time.time())}.jpg"
        
        with open(img_name, "wb") as f:
            f.write(raw)
            
        bot.delete_message(msg.chat.id, wait_msg.message_id)

        # Slayd sonini so'rash
        ask_msg = bot.send_message(msg.chat.id, "🔢 Nechta slayd yaratishni xohlaysiz? (Iltimos raqam kiriting, masalan: 5)")
        bot.register_next_step_handler(ask_msg, prepare_slides, img_name, is_image=True)

    except Exception as e:
        bot.send_message(msg.chat.id, f"❌ Xatolik yuz berdi: {e}")


@bot.message_handler(content_types=["text"])
def handle_text(msg):
    if msg.text.startswith("/"):
        return
        
    ask_msg = bot.reply_to(msg, "🔢 Nechta slayd yaratishni xohlaysiz? (Iltimos raqam kiriting, masalan: 5)")
    bot.register_next_step_handler(ask_msg, prepare_slides, msg.text, is_image=False)


def prepare_slides(msg, input_data, is_image):
    try:
        slide_count = int(msg.text.strip())
        if slide_count < 1 or slide_count > 20:
            raise ValueError()
    except ValueError:
        bot.send_message(msg.chat.id, "⚠️ Noto'g'ri raqam! Iltimos 1 dan 20 gacha bo'lgan to'g'ri raqam yozing va boshidan yuboring.")
        if is_image and os.path.exists(input_data):
            os.remove(input_data)
        return

    wait_msg = bot.send_message(msg.chat.id, f"⏳ Qabul qildim! {slide_count} ta slayd yasalmoqda, rasmlar yuklanmoqda kuting...")
    process_and_send(msg.chat.id, wait_msg.message_id, input_data, is_image, slide_count)


def process_and_send(chat_id, wait_message_id, input_data, is_image, slide_count):
    output_name = f"slayd_{chat_id}_{int(time.time())}"
    
    try:
        pptx_path = generate_pptx(
            input_data=input_data,
            is_image=is_image,
            output_name=output_name,
            slide_count=slide_count
        )

        with open(pptx_path, "rb") as f:
            bot.send_document(
                chat_id, f,
                caption=f"✅ *Slaydlaringiz tayyor! ({slide_count} ta slayd)*\nAniq formatda yig'ildi.",
                parse_mode="Markdown"
            )
            
        bot.delete_message(chat_id, wait_message_id)
        os.remove(pptx_path)

    except Exception as e:
        bot.send_message(chat_id, f"❌ Taqdimotni yasashda muammo chiqdi:\n`{e}`", parse_mode="Markdown")
        
    finally:
        if is_image and os.path.exists(input_data):
            try:
                os.remove(input_data)
            except:
                pass

import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

# ... (Oldingi kodlar o'zgarmaydi)

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

def run_health_server():
    port = int(os.environ.get("PORT", 10000))
    server_address = ('', port)
    httpd = HTTPServer(server_address, HealthCheckHandler)
    print(f"  Health check server {port}-portda ishga tushdi.")
    httpd.serve_forever()

if __name__ == "__main__":
    print("=" * 50)
    print("  Toza Slayd Bot - ishga tushdi!")
    print("=" * 50)
    
    # Health check serverini alohida thread-da ishga tushiramiz
    threading.Thread(target=run_health_server, daemon=True).start()
    
    # Bot polling-ni asosiy thread-da ishga tushiramiz
    bot.infinity_polling(timeout=30, long_polling_timeout=20)
