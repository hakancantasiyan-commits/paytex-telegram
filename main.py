
import os
import logging
import asyncio

from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.utils import get_peer_id

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

try:
    API_ID = int(os.environ["TELEGRAM_API_ID"])
    API_HASH = os.environ["TELEGRAM_API_HASH"]
    SESSION = os.environ["TELEGRAM_SESSION"]
except KeyError as error:
    raise RuntimeError(
        f"Hostless ortam degiskeni eksik: {error}"
    ) from error

TARGET_CHANNEL = "paytextasarim"
WHATSAPP_LINK = "https://wa.me/905527203981"

SOURCE_CHANNELS = [
    "dadaligiyim",
    "qofretekstiltoptantelegram",
    "solba_toptan",
    "soleelife",
    "maqasdesign",
    "pelestia",
    "Renvatopta",
    "meermoda",
    "merilinetoptan",
]

client = TelegramClient(
    StringSession(SESSION),
    API_ID,
    API_HASH,
)

# Ayni albümü tekrar işlememek için
processed_groups = set()


async def main():
    await client.start()

    target = await client.get_entity(TARGET_CHANNEL)
    sources = [
        await client.get_entity(channel)
        for channel in SOURCE_CHANNELS
    ]

    source_ids = {
        get_peer_id(source) for source in sources
    }

    @client.on(events.Album(chats=sources))
    async def forward_album(event):
        messages = event.messages
        if not messages:
            return

        group_id = messages[0].grouped_id
        key = (event.chat_id, group_id)

        if key in processed_groups:
            return

        processed_groups.add(key)

        original_caption = next(
            (m.message for m in messages if m.message),
            "",
        )

        caption = (
            f"{original_caption}\n\n"
            f"📲 Sipariş ve bilgi için WhatsApp:\n"
            f"{WHATSAPP_LINK}"
        ).strip()

        media = [
            m.media for m in messages
            if m.media and (m.photo or m.video)
        ]

        if not media:
            return

        try:
            await client.send_file(
                target,
                media,
                caption=[caption] + [""] * (len(media) - 1),
            )
            logging.info(
                "Album aktarıldı: %s medya, kaynak %s",
                len(media),
                event.chat_id,
            )
        except Exception:
            logging.exception("Album aktarılamadı")

    @client.on(events.NewMessage(chats=sources))
    async def forward_single(event):
        message = event.message

        if message.grouped_id:
            return

        if not (message.photo or message.video):
            return

        original_caption = message.message or ""
        caption = (
            f"{original_caption}\n\n"
            f"📲 Sipariş ve bilgi için WhatsApp:\n"
            f"{WHATSAPP_LINK}"
        ).strip()

        try:
            await client.send_file(
                target,
                message.media,
                caption=caption,
            )
            logging.info(
                "Fotoğraf/video aktarıldı. Kaynak: %s",
                event.chat_id,
            )
        except Exception:
            logging.exception("Medya aktarılamadı")

    logging.info(
        "Paytex Tasarım sistemi çalışıyor: fotoğraf, video ve albümler."
    )

    await client.run_until_disconnected()


if __name__ == "__main__":
    with client:
        client.loop.run_until_complete(main())
        
