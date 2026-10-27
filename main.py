import os
import logging
import asyncio

from telethon import TelegramClient, events
from telethon.sessions import StringSession

# Log ayarlari
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Hostless ortam degiskenleri
try:
    API_ID = int(os.environ["TELEGRAM_API_ID"])
    API_HASH = os.environ["TELEGRAM_API_HASH"]
    SESSION = os.environ["TELEGRAM_SESSION"]
except KeyError as error:
    raise RuntimeError(
        f"Hostless ortam degiskeni eksik: {error}"
    ) from error

# Kanal ayarlari
TARGET_CHANNEL = "paytextasarim"  # @ olmadan

WHATSAPP_LINK = "https://wa.me/905527203981"

SOURCE_CHANNELS = [
    "dadaligiyim",
    "qofretekstiltoptantelegram",
    "solba_toptan",
    "soleelife",
    "maqasdesign",
    "pelestia",
    "renvatopta",
    "meermoda",
    "merilinetoptan",
]

client = TelegramClient(
    StringSession(SESSION),
    API_ID,
    API_HASH,
)

# Her kaynak kanal icin fotograflari saymak icin
# yapi: { chat_id: sayac_int }
photo_counters = {}
THRESHOLD = 5  # Her 5 fotograftan sonra 1 defa WhatsApp mesaji


async def main():
    await client.start()

    target = await client.get_entity(TARGET_CHANNEL)
    sources = [await client.get_entity(channel) for channel in SOURCE_CHANNELS]

    @client.on(events.NewMessage(chats=sources))
    async def forward_photo(event):
        message = event.message

        # Yalnizca fotografli gonderileri isliyoruz
        if not message.photo:
            return

        chat_id = event.chat_id
        source_name = (
            getattr(event.chat, "username", None)
            or getattr(event.chat, "title", "bilinmeyen")
        )

        # 1) Fotografı hemen Paytex kanalina aktar (whatsapp link YOK)
        original_caption = message.message or ""
        caption = original_caption.strip() or None

        try:
            await client.send_file(
                target,
                message.photo,
                caption=caption,
            )
            logging.info(
                "Fotograf aktarildi. Kaynak kanal: %s (id=%s)",
                source_name,
                chat_id,
            )
        except Exception:
            logging.exception("Fotograf aktarilamadi")
            return

        # 2) Bu kanal icin fotograf sayacini arttir
        current = photo_counters.get(chat_id, 0) + 1
        photo_counters[chat_id] = current
        logging.info(
            "Sayac guncellendi. Kaynak kanal: %s (id=%s), count=%s",
            source_name,
            chat_id,
            current,
        )

        # 3) Sayac esige ulasinca (5 foto) 1 defalik whatsapp mesaji gonder
        if current >= THRESHOLD:
            text = (
                f"Son {THRESHOLD} urun paylasimi '{source_name}' kanalindan geldi.\n\n"
                f"📲 Sipariş ve bilgi için WhatsApp:\n"
                f"{WHATSAPP_LINK}"
            )
            try:
                await client.send_message(target, text)
                logging.info(
                    "WhatsApp mesaji gonderildi. Kaynak kanal: %s (id=%s), count=%s",
                    source_name,
                    chat_id,
                    current,
                )
            except Exception:
                logging.exception("WhatsApp mesaji gonderilemedi")

            # Sayaci sifirla
            photo_counters[chat_id] = 0

    logging.info(
        "Paytex Tasarim aktarim sistemi calisiyor (her 5 fotografta 1 wp mesaji)."
    )
    await client.run_until_disconnected()


if __name__ == "__main__":
    with client:
        client.loop.run_until_complete(main())
