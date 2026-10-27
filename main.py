
import os
import logging
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# Telegram API bilgileri ortam değişkenlerinden alınır
API_ID = int(os.environ["TELEGRAM_API_ID"])
API_HASH = os.environ["TELEGRAM_API_HASH"]
SESSION = os.environ["TELEGRAM_SESSION"]

TARGET_CHANNEL = "paytextasarim"
WHATSAPP_LINK = "https://wa.me/905527203981"

SOURCE_CHANNELS = [
    "dadaligiyim",
    "qofretekstiltoptantelegram",
    "solba_toptan",
    "soleelife",
    "maqasdesign",
    "pelestia",
]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

client = TelegramClient(StringSession(SESSION), API_ID, API_HASH)


async def main():
    await client.start()

    target = await client.get_entity(TARGET_CHANNEL)
    sources = [
        await client.get_entity(channel)
        for channel in SOURCE_CHANNELS
    ]

    @client.on(events.NewMessage(chats=sources))
    async def forward_photo(event):
        message = event.message

        # Yalnızca fotoğraf içeren gönderileri aktar
        if not message.photo:
            return

        original_caption = message.message or ""
        caption = (
            f"{original_caption}\n\n"
            f"📲 Sipariş ve bilgi için WhatsApp:\n{WHATSAPP_LINK}"
        ).strip()

        try:
            await client.send_file(
                target,
                message.photo,
                caption=caption,
            )
            logging.info("Fotoğraf aktarıldı: %s", event.chat_id)

        except Exception:
            logging.exception("Fotoğraf aktarılırken hata oluştu")

    logging.info("Paytex Tasarım aktarım sistemi çalışıyor.")
    await client.run_until_disconnected()


with client:
    client.loop.run_until_complete(main())
