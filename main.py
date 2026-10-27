
import os
import logging
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# Telegram API bilgileri ortam değişkenlerinden alınır
API_ID = int(os.environ["30759251"])
API_HASH = os.environ["0e42bd51271da309534ee34c7c799eab"]
SESSION = os.environ["1BJWap1wBu5Qdnxj7GlNCLEKhbYqr-FSNV_6mLjOt-mt8aggQi61Np7lucK_2qDDneomeOryVzKnbN1M0qbzDFbxJxxHfmX949l45jXd4KJk4ZzGr3dYtPUidGoAKpHS6AL7yWkUISfFD8sEXig781TpGQ1v663DHPNQ52r6urt2-7cVQ2z334DF-AMC9fnkmS38Vxbi68ye9__Wn0zc2C6m-gALHVrRs2T-CKwvRlrEoVut9TSTZ-JWEdyIIdZT_TcyJOqr0G0MO0o9j4oVUPjk36OzIKtXMrKDt3O2-AWF9PVKVQAuguPJz7kN6SbIBckUfIpTGB8-eiwEXlr7Fai03WVq4KlM="]

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
