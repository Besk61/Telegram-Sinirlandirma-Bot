from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import time

TOKEN = "8038142321:AAFbEoilri2DfDQTK-OccpZ4C3RD4C8M7qY"  # Bot tokenini buraya yaz
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Konu bazlı mesaj gönderme süreleri (saniye cinsinden)
TOPIC_LIMITS = {
    3: 3600,  # Örnek Konu ID: 1 saat (3600 saniye)
    771: 15,
    4: 15,
}

user_last_message_time = {}  # Kullanıcıların mesaj zamanlarını saklar

# /sendbotkey komutunu işleyen handler
@dp.message_handler(commands=['sendbotkey'])
async def send_bot_key(message: types.Message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    topic_id = message.message_thread_id  # Mesajın пришла konu ID

    # Kullanıcının admin olup olmadığını kontrol et
    chat_member = await bot.get_chat_member(chat_id, user_id)
    if chat_member.status not in ["administrator", "creator"]:
        await message.reply("Bu komutu sadece adminler kullanabilir!")
        return

    # Inline buton oluştur
    keyboard = InlineKeyboardMarkup()
    start_button = InlineKeyboardButton(text="Bota Başla", url=f"https://t.me/{bot._me.username}?start=from_topic")
    keyboard.add(start_button)

    # Topic içinde butonlu mesaj gönder
    await bot.send_message(
        chat_id=chat_id,
        message_thread_id=topic_id,
        text="Bota katılmak için aşağıdaki butona tıklayın!",
        reply_markup=keyboard
    )

# /start komutunu işleyen handler
@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    user_id = message.from_user.id
    # URL'deki parametreleri kontrol et
    if message.get_args() == "from_topic":
        await bot.send_message(
            user_id,
            f"Hoş geldiniz, {message.from_user.first_name}! Topic üzerinden geldiniz, artık botu kullanabilirsiniz."
        )
    else:
        await bot.send_message(
            user_id,
            f"Merhaba, {message.from_user.first_name}! Botu kullanmaya başlayabilirsiniz."
        )

# Mesaj kısıtlama handler'ı
@dp.message_handler()
async def restrict_messages(message: types.Message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    topic_id = message.message_thread_id  # Mesajın geldiği konu ID

    # Kullanıcının admin olup olmadığını kontrol et
    chat_member = await bot.get_chat_member(chat_id, user_id)
    if chat_member.status in ["administrator", "creator"]:
        return  # Adminse sınır uygulanmaz

    if topic_id in TOPIC_LIMITS:
        message_interval = TOPIC_LIMITS[topic_id]  # O konunun limiti
        last_time = user_last_message_time.get((user_id, topic_id), 0)
        current_time = time.time()

        if current_time - last_time < message_interval:
            await message.delete()  # Kullanıcının mesajını sil
            try:
                if(message_interval>60):
                    await bot.send_message(
                        user_id,
                        f"⚠️ {message.from_user.first_name}, bu konuda {message_interval // 60} dakika beklemen gerekiyor! {(message_interval - (current_time - last_time)) // 60} dakika beklemelisin."
                    )
                else:
                    await bot.send_message(
                        user_id,
                        f"⚠️ {message.from_user.first_name}, bu konuda {message_interval} saniye beklemen gerekiyor! {str(message_interval - (current_time - last_time))[:2]} saniye beklemelisin."
                    )
            except:
                pass  # Eğer bot kullanıcıya özel mesaj gönderemezse hata almamak için
            return

        user_last_message_time[(user_id, topic_id)] = current_time  # Mesaj zamanını kaydet

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)