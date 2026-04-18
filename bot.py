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

# ... (Pastdagi barcha handlerlar o'zgarishsiz qoladi)

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

def run_health_server():
    port = int(os.environ.get("PORT", 10000))
    server_address = ('', port)
    try:
        httpd = HTTPServer(server_address, HealthCheckHandler)
        print(f"  Health check server {port}-portda ishga tushdi.")
        httpd.serve_forever()
    except Exception as e:
        print(f"  [Server Xatosi] {e}")

if __name__ == "__main__":
    print("=" * 50)
    print("  Toza Slayd Bot - ishga tushdi!")
    print("=" * 50)
    
    # Health check tizimi alohida oqimda
    threading.Thread(target=run_health_server, daemon=True).start()
    
    # Botni ishga tushirish
    bot.infinity_polling(timeout=30, long_polling_timeout=20)
