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

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b"Bot is alive and running!")

    def log_message(self, format, *args):
        # Render loglarini toza saqlash uchun HTTP so'rovlarni terminalga chiqarmaymiz
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
    print("  Toza Slayd Bot - Render-ga tayyorlanmoqda...")
    print("=" * 50)
    
    # Health check tizimi alohida oqimda
    threading.Thread(target=run_health_server, daemon=True).start()
    
    # Botni ishga tushirish (xatoliklarga chidamli rejimda)
    try:
        print("[OK] Bot polling boshladi...")
        bot.infinity_polling(timeout=30, long_polling_timeout=20)
    except Exception as e:
        print(f"[Xato] Bot poller-da xatolik yuz berdi: {e}")

