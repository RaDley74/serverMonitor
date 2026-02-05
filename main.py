import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import psutil
import platform
from datetime import datetime
from aiogram.utils.keyboard import ReplyKeyboardBuilder
import dotenv
import os
from pathlib import Path
import socket


dotenv.load_dotenv()






API_TOKEN = os.getenv("API_TOKEN")

# Читаем строку из .env и превращаем её в список чисел
# В .env файле укажите их через запятую: ADMIN_IDS=12345,67890
ADMIN_IDS = [int(id.strip()) for id in os.getenv("ADMIN_IDS", "").split(",") if id.strip()]


if not ADMIN_IDS:
    print("⚠️ ВНИМАНИЕ: Список администраторов пуст! Проверьте ADMIN_IDS в .env")
    raw_admin_ids = os.getenv("ADMIN_IDS")
    print(f"DEBUG: Содержимое ADMIN_IDS из .env: '{raw_admin_ids}'") # Добавьте это
    
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

def get_system_status():
    # CPU
    hostname = socket.gethostname()
    cpu_usage = psutil.cpu_percent(interval=1)
    hostname = socket.gethostname()
    # RAM
    ram = psutil.virtual_memory()
    ram_used_gb = ram.used / (1024**3)
    ram_total_gb = ram.total / (1024**3)
    
    # Disk
    disk_path = os.getenv("DISK_PATH", "/")
    disk = psutil.disk_usage(disk_path)
    
    # Network
    net_1 = psutil.net_io_counters()
    import time; time.sleep(1)
    net_2 = psutil.net_io_counters()
    
    upload = (net_2.bytes_sent - net_1.bytes_sent) / 1024
    download = (net_2.bytes_recv - net_1.bytes_recv) / 1024

    uptime = datetime.now() - datetime.fromtimestamp(psutil.boot_time())
    
    return (
        f"🏷 **Server:** {hostname}\n"
        f"🖥 **CPU Usage:** {cpu_usage}%\n"
        f"🧠 **RAM:** {ram.percent}% ({ram_used_gb:.2f} GB / {ram_total_gb:.2f} GB)\n"
        f"💾 **Disk:** {disk.percent}% ({disk.free // 1024**3} GB free)\n"
        f"🌐 **Upload:** {upload:.1f} KB/s\n"
        f"📥 **Download:** {download:.1f} KB/s\n"
        f"⏱ **Uptime:** {str(uptime).split('.')[0]}"
    )

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    # Проверка: ID пользователя есть в списке администраторов?
    if message.from_user.id not in ADMIN_IDS: 
        return
    
    builder = ReplyKeyboardBuilder()
    builder.row(types.KeyboardButton(text="📊 Статус сервера"))
    
    await message.answer("Мониторинг запущен", reply_markup=builder.as_markup(resize_keyboard=True))

@dp.message(lambda message: message.text == "📊 Статус сервера")
async def send_status(message: types.Message):
    # Проверка прав доступа
    if message.from_user.id not in ADMIN_IDS: 
        return
    
    status_text = get_system_status()
    await message.answer(status_text, parse_mode="Markdown")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        print(f"--- Бот запущен (Админов: {len(ADMIN_IDS)}) ---")
        print(f"Администраторы: {ADMIN_IDS}")
        asyncio.run(main())
    except Exception as e:
        print(f"Ошибка при запуске: {e}")