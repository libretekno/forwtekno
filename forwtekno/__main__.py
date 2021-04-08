import logging
import asyncio
from aiogram.types.input_media import MediaGroup
from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils.executor import start_webhook

from forwtekno import (
    API_TOKEN, ALLOWED_TYPES,
    FROM_CHANNEL, TO_CHANNEL, TO_CAPTION,
    PORT,  WEBHOOK_PATH, WEBHOOK_URL, HOST
)

logger = logging.getLogger(__name__)

bot = Bot(token=API_TOKEN)
dispatcher = Dispatcher(bot, storage=MemoryStorage())


async def media_group_sender(message, state):
    async with state.proxy() as data:
        group = MediaGroup()
        for msg in data[message.media_group_id]:

            if msg.photo:
                file_id = msg.photo[-1].file_id
            else:
                file_id = msg[msg.content_type].file_id

            group.attach({
                'media': file_id,
                'type': msg.content_type,
                'caption': TO_CAPTION
            })

        await bot.send_media_group(TO_CHANNEL, media=group, disable_notification=False)


async def channel_message_handler(message):
    await message.copy_to(TO_CHANNEL, TO_CAPTION, disable_notification=False)


async def channel_media_group_handler(message, state):
    async with state.proxy() as data:
        group_id = message.media_group_id
        if group_id not in data:
            asyncio.get_event_loop().call_later(
                5, asyncio.create_task, media_group_sender(message, state)
            )

        data.setdefault(group_id, []).append(message)


dispatcher.register_channel_post_handler(
    channel_media_group_handler,
    is_media_group=True,
    chat_id=FROM_CHANNEL,
    is_forwarded=False,
    content_types=ALLOWED_TYPES
)
dispatcher.register_channel_post_handler(
    channel_message_handler,
    is_media_group=False,
    chat_id=FROM_CHANNEL,
    is_forwarded=False,
    content_types=ALLOWED_TYPES
)


async def on_startup(dispatcher):
    await bot.set_webhook(WEBHOOK_URL)


start_webhook(
    dispatcher=dispatcher,
    webhook_path=WEBHOOK_PATH,
    on_startup=on_startup,
    host=HOST,
    port=PORT,
)
