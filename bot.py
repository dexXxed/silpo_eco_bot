from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ParseMode
from aiogram.types.message import ContentType
import logging
import os
from pyzbar.pyzbar import decode
import cv2
import pandas as pd
from dotenv import load_dotenv
from tinydb import TinyDB, Query

load_dotenv()

logging.basicConfig(level=logging.INFO)

bot = Bot(token=os.getenv('TOKEN'))
dp = Dispatcher(bot)
db = TinyDB('db.json')

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
    response = """Привіт 🤗 
    
Я  🤖, який допоможе посортувати твоє сміття!

Натисни:
/how_it_works для розуміння логіки роботи 🤖 та дій користувача
/trash_info для отримання списку допустимої вторсировини ♻
/prepare_trash відповідає на питання <b>"Як підготувати вторсировину для переробки?"</b> 🏡
"""
    user = Query()
    if not db.search(user.username == message.from_user.id):
        db.insert({'username': message.from_user.id,
                   'metal': 0,
                   'paper': 0,
                   'glass': 0,
                   'plastic': 0})
    await message.answer(response, parse_mode=ParseMode.HTML)\



@dp.message_handler(commands=['how_it_works'])
async def how_it_works(message: types.Message):
    response = """Відскануйте штрихкоди тар - ми підкажемо чи можна їх переробити та як відсортувати. 📱
    
1. До приїзду кур’єра готуєте сміття, перетворивши його на вторинну сировину за цією інструкцією - /prepare_trash

2. Робите замовлення на shop.silpo.ua з плановою доставкою на зручний день та час ⏲

3. Забираєте своє замовлення і заодно прощаєтеся з відходами ♻

4. Знаєте, що вторсировина потрапить на станцію SilpoRecycling від того почуваєтеся краще. 🏭

5. Отримаєте бонуси на власний рахунок! 🎁

"""
    await message.answer(response, parse_mode=ParseMode.HTML)


@dp.message_handler(commands=['trash_info'])
async def trash_info(message: types.Message):
    response = """Станція у вашому місті може прийняти:

ПАПІР 📰:
Тетрапак, паперова упаковка, картон, паперові пакети та стаканчики.

ПЛАСТИК ♳:
Прозорі пляшки ПЕТ, пляшки від побутової хімії HDPE, кришечки від пляшок, стретч-плівка

МЕТАЛ 🥫:
Алюмінієві банки

СКЛО 🍾:
Скляні пляшки
"""
    await message.answer(response, parse_mode=ParseMode.HTML)


@dp.message_handler(commands=['prepare_trash'])
async def trash_info(message: types.Message):
    response = """<b>ЯК ПІДГОТУВАТИ?</b>
Аби зі сміття зробити вторинну сировину, виконуйте три прості правила:

1. ВІДСОРТОВУЙТЕ ♻
Скло, метал, папір та пластик складайте окремо. Більш детально про речі, які можна (і не можна) здати у вашому місті, прочитайте вище. Не кладіть до вторсировини «заборонених» предметів, аби це було дійсно ефективно та екологічно.

2. МИЙТЕ 🌊
Станція може прийняти лише чисті та сухі упаковки. Якщо у вас немає можливості вимити щось — краще викинути це до загального смітника, ніж забруднити всі відсортовані відходи та зробити їх непридатними до здачі.

3. СТИСКАЙТЕ 🧳
Папір, картон, бляшанки та пляшки старайтеся якомога сильніше стиснути, аби розмістити відходи компактно. Об’єм вторсировини не має перевищувати 60 літрів (це як мішок цукру).
"""
    await message.answer(response, parse_mode=ParseMode.HTML)
    await bot.send_photo(message.from_user.id, open('./photos/1.png', 'rb'), caption='1. ВІДСОРТОВУЙТЕ ♻')
    await bot.send_photo(message.from_user.id, open('./photos/2.png', 'rb'), caption='2. МИЙТЕ 🌊')
    await bot.send_photo(message.from_user.id, open('./photos/3.png', 'rb'), caption='3. СТИСКАЙТЕ 🧳')


@dp.message_handler(content_types=ContentType.PHOTO)
async def get_type_of_barcode(message: types.Message):
    await message.photo[-1].download(destination_file=f'photos/{message.photo[1].file_id}.jpg')

    bar_code = barcode_reader(f'photos/{message.photo[1].file_id}.jpg')
    os.remove(f'photos/{message.photo[1].file_id}.jpg')

    if bar_code != '':
        if not barcodes[barcodes['id'].str.contains(bar_code)].empty:
            user = Query()
            db.update({f'{barcodes[barcodes["id"].str.contains(bar_code)].min()["class"]}': db.search(user.username == message.from_user.id)[0][f'{barcodes[barcodes["id"].str.contains(bar_code)].min()["class"]}'] + 1 }, user.username == message.from_user.id)

            await message.reply(f"Название товара: {barcodes[barcodes['id'].str.contains(bar_code)].min()['name']}\n"
                                f"Тип товара: {barcodes[barcodes['id'].str.contains(bar_code)].min()['class']}",
                                parse_mode=ParseMode.HTML)
        else:
            await message.reply('Такой товар не перерабатывается!')
    else:
        await message.reply("Повторите фото, считывание не удалось!")


@dp.message_handler(commands=['stats'])
async def stats(message: types.Message):
    user = Query()
    await message.reply(f"""Вами було накопичено загалом {db.search(user.username == message.from_user.id)[0]['paper'] + db.search(user.username == message.from_user.id)[0]['plastic'] + db.search(user.username == message.from_user.id)[0]['metal'] + db.search(user.username == message.from_user.id)[0]['glass']} перерабатываемых продуктов: 

ПАПЕРУ 📰: {db.search(user.username == message.from_user.id)[0]['paper']} шт.

ПЛАСТИК ♳: {db.search(user.username == message.from_user.id)[0]['plastic']} шт.

МЕТАЛ 🥫: {db.search(user.username == message.from_user.id)[0]['metal']} шт.

СКЛО 🍾: {db.search(user.username == message.from_user.id)[0]['glass']} шт.
""")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=False)
