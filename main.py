
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
    API_ID = int(os.environ["30759251"])
    API_HASH = os.environ["0e42bd51271da309534ee34c7c799eab"]
    SESSION = os.environ["1BJWap1wBu5Qdnxj7GlNCLEKhbYqr-FSNV_6mLjOt-mt8aggQi61Np7lucK_2qDDneomeOryVzKnbN1M0qbzDFbxJxxHfmX949l45jXd4KJk4ZzGr3dYtPUidGoAKpHS6AL7yWkUISfFD8sEXig781TpGQ1v663DHPNQ52r6urt2-7cVQ2z334DF-AMC9fnkmS38Vxbi68ye9__Wn0zc2C6m-gALHVrRs2T-CKwvRlrEoVut9TSTZ-JWEdyIIdZT_TcyJOqr0G0MO0o9j4oVUPjk36OzIKtXMrKDt3O2-AWF9PVKVQAuguPJz7kN6SbIBckUfIpTGB8-eiwEXlr7Fai03WVq4KlM="]
except KeyError as error:
    raise RuntimeError(
        f"Hostless ortam degiskeni eksik: {error}"
    ) from error

# Kanal ayarlari
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

client = TelegramClient(
    StringSession(SESSION),
    API_ID,
    API_HASH,
)


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

        # Yalnizca fotografli gonderileri aktar
        if not message.photo:
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
                message.photo,
                caption=caption,
            )
            logging.info(
                "Fotograf aktarildi. Kaynak: %s",
                event.chat_id,
            )
        except Exception:
            logging.exception("Fotograf aktarilamadi")

    logging.info("Paytex Tasarim aktarim sistemi calisiyor.")
    await client.run_until_disconnected()


if __name__ == "__main__":
    with client:
        client.loop.run_until_complete(main())
