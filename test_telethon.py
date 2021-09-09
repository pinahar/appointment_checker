import pytesseract
import cv2
import numpy as np
import logging
from telethon import TelegramClient, events, utils
from uuid import uuid4

logging.basicConfig(
    filename='telethon.log',
    format='%(asctime)s\t%(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S'
)

session = 'visa_bot'
api_id = '<INSERT HERE>'
api_hash = '<INSERT HERE>'
client = TelegramClient(session, api_id, api_hash).start()

def image_to_string(file):
    img = cv2.imread(file)
    gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    threshold_img = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    return pytesseract.image_to_string(threshold_img, lang='eng', config='--psm 1')

def is_image(media):
    type_ = None
    try:
        if 'image' in media.document.mime_type:
            type_ = 'image'
    except:
        pass

    try:
        if media.photo:
            type_ = 'image'
    except:
        pass

    return type_ == 'image'

async def handle_media(event):
    if not is_image(event.media):
        logging.info(f'Not a valid image, not forwarding')
        return

    file_name = str(uuid4())
    file = await client.download_media(event.media, file_name)
    logging.info(f'{file} downloaded')
    text = image_to_string(file).lower()
    logging.info(f'Actual text - {text}')

    if 'vac' in text:
        logging.info(f'Image contains vac, not forwarding')
        return
    elif 'no appointments' in text:
        logging.info(f'Image contains no appointments, not forwarding')
        return

    logging.info('Forwarding media to group as it seems interesting')
    await client.forward_messages(-503730613, event.id, event.chat_id)

async def handle_text(event):
    message_text = event.text.lower()
    if 'not available' in message_text:
        return
    elif '?' in message_text:
        return
    elif 'available' not in message_text:
        return
    elif 'del' not in message_text and 'mum' not in message_text and 'hyd' not in message_text \
      and 'kol' not in message_text and 'che' not in message_text and 'chn' not in message_text:
        return

    logging.info('Forwarding text to group as it seems interesting')
    await client.forward_messages(-503730613, event.id, event.chat_id)

@client.on(events.NewMessage())
async def handler(event):
    if event.out or event.chat_id != -1001371184682:
        return

    sender = await event.get_sender()
    name = utils.get_display_name(sender)

    logging.info(f'{name} sent {event.text or "media"}')
    if event.media:
        await handle_media(event)
    else:
        await handle_text(event)

with client:
    print('(Press Ctrl+C to stop this)')
    client.run_until_disconnected()
