from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ParseMode
from aiogram.types.message import ContentType
import logging
import os
from pyzbar.pyzbar import decode
import cv2
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)

bot = Bot(token=os.getenv('TOKEN'))
dp = Dispatcher(bot)
barcodes = pd.read_csv('barcodes.csv')


def barcode_reader(image):
    global barcode

    detected_barcodes = decode(cv2.imread(image))

    if not detected_barcodes:
        return ''
    else:
        # Traverse through all the detected barcodes in image
        for barcode in detected_barcodes:
            if barcode.data != '':
                return str(barcode.data.decode("utf-8"))


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    response = """Привіт!
    
Пожалуйста, отправьте мне фото штрихкода и в описании фото "Название продукта - тип его переработки" 🤗"""
    await message.answer(response, parse_mode=ParseMode.HTML)


@dp.message_handler(content_types=ContentType.PHOTO)
async def get_type_of_barcode(message: types.Message):
    await message.photo[-1].download(destination_file=f'photos/{message.photo[1].file_id}.jpg')

    bar_code = barcode_reader(f'photos/{message.photo[1].file_id}.jpg')
    os.remove(f'photos/{message.photo[1].file_id}.jpg')

    if bar_code != '':
        if not barcodes[barcodes['id'].str.contains(bar_code)].empty:
            await message.reply(f"Название товара: {barcodes[barcodes['id'].str.contains(bar_code)].min()['name']}\n"
                                f"Тип товара: {barcodes[barcodes['id'].str.contains(bar_code)].min()['class']}",
                                parse_mode=ParseMode.HTML)
        else:
            await message.reply('Такой товар не перерабатывается!')
    else:
        await message.reply("Повторите фото, считывание не удалось!")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=False)
