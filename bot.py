import os
import time
import telebot
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from dotenv import load_dotenv
from ppt_generator import generate_pptx

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not BOT_TOKEN:
    print("[XATO] TELEGRAM_BOT_TOKEN topilmadi!")
    exit(1)

bot = telebot.TeleBot(BOT_TOKEN)

# Foydalanuvchi ma'lumotlarini saqlash uchun lug'at (ixtiyoriy, hozircha kerak emas)
user_data = {}

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Salom! Menga fizika oid rasm yoki matn yuboring, men sizga chiroyli PowerPoint taqdimot yasab beraman. 🚀")

@bot.message_handler(content_types=['photo', 'text'])
def handle_message(message):
    chat_id = message.chat.id
    sent_msg = bot.send_message(chat_id, "Iltimos, kuting. Taqdimot tayyorlanmoqda... ⏳")
    
    try:
        is_image = False
        input_data = ""
        
        if message.content_type == 'photo':
            is_image = True
            file_info = bot.get_file(message.photo[-1].file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            input_data = f"temp_image_{chat_id}_{int(time.time())}.jpg"
            with open(input_data, "wb") as f:
                f.write(downloaded_file)
        else:
            input_data = message.text

        # PPTX yaratish (Slaydlar soni: 5 ta)
        output_name = f"taqdimot_{chat_id}_{int(time.time())}"
        pptx_file = generate_pptx(input_data, is_image, output_name, slide_count=5)
        
        # Faylni yuborish
        with open(pptx_file, "rb") as f:
            bot.send_document(chat_id, f, caption="Mana sizning taqdimotingiz! ✨")
        
        # Vaqtinchalik fayllarni o'chirish
        if os.path.exists(pptx_file):
            os.remove(pptx_file)
        if is_image and os.path.exists(input_data):
            os.remove(input_data)
            
        bot.delete_message(chat_id, sent_msg.message_id)
        
    except Exception as e:
        bot.reply_to(message, f"Kechirasiz, xatolik yuz berdi: {e}")
        print(f"[ERROR] {e}")

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b"Bot is alive and running!")

    def log_message(self, format, *args):
        return

def run_health_server():
    port = int(os.environ.get("PORT", 10000))
    server_address = ('0.0.0.0', port)
    try:
        httpd = HTTPServer(server_address, HealthCheckHandler)
        print(f"[OK] Health check server {port}-portda ishga tushdi.")
        httpd.serve_forever()
    except Exception as e:
        print(f"[Xato] Health check serverda muammo: {e}")

if __name__ == "__main__":
    print("=" * 50)
    print("  Toza Slayd Bot - Render-da ishga tushdi!")
    print("=" * 50)
    
    threading.Thread(target=run_health_server, daemon=True).start()
    
    try:
        print("[OK] Bot polling boshladi...")
        bot.infinity_polling(timeout=30, long_polling_timeout=20)
    except Exception as e:
        print(f"[Xato] Bot poller-da xatolik yuz berdi: {e}")


