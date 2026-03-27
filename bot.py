#Работа бота
import os
from dotenv import load_dotenv
#Загрузите свой API полученный в BotFather
load_dotenv()
TOKEN = os.getenv("YOUR_TOKEN_BOT")

import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from logic import get_weather_info
from menu import *

#Загрузка вашего токена и преобразования класса Dispatcher в переменную для использования декоратора
bot = Bot(token=TOKEN)
dp = Dispatcher()

#Все кнопки
Buttons = ["Настройки", "Выбрать время", "Назад", "Назад в настройки", "На несколько дней вперед", "Написать в поддержку!"]

#При команде или сообщении(@dp.message(Command or F.text)), выполнять функцию независимо от того завершилась ли предыдущая функция (async),
#ожидая пока она завершится (await), это нужно чтобы ботом могли пользоваться несколько пользователей одновременно
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привет ! Напиши город или выбери в меню:", reply_markup=main_menu())

@dp.message(F.text == "Настройки")
async def open_settings(message: types.Message):
    await message.answer("Настройки:", reply_markup=help_menu())

@dp.message(F.text == "Выбрать время")
async def open_settings(message: types.Message):
    await message.answer("Напиши свой город и час через запятую.\nНапример: Москва, 15", reply_markup=hours_menu())

@dp.message(F.text == "Назад")
async def back_to_main(message: types.Message):
    await message.answer("Главное меню", reply_markup=main_menu())

@dp.message(F.text == "Назад в настройки")
async def back_to_main(message: types.Message):
    await message.answer("Главное меню", reply_markup=help_menu())


@dp.message(F.text == "На несколько дней вперед")
async def info_days(message: types.Message):
    await message.answer(
        "Чтобы получить прогноз на несколько дней, напишите город и количество дней через пробел.\n"
        "Например: Улан-удэ 5",
        reply_markup=days_menu(),
    )

@dp.message(F.text == "Назад в выбор времени")
async def info_days(message: types.Message):
    await message.answer(
        "Выбор времени",
        reply_markup=hours_menu(),
    )

@dp.message(F.text)
async def handle_weather(message: types.Message):
    #Если сообщение заданно в menu.py - возвращаемся
    if message.text in Buttons:
        return
    #Очищаем строку и сохраняем в переменную
    text = message.text.strip()

    #Разделяем строку(Для города и количества дней)
    parts = text.split()

    #Если в сообщении присутствует ",", то делаем алгоритм ниже!
    if "," in text:
        #Сперва заносим город в переменную, а потом час, разделяя по запятой
        city_name, hour_val = text.split(",")
        #Очищаем строку и проверяем является ли переменная числом
        if hour_val.strip().isdigit():
            #Вставляем полученное название города и час в функцию(из файла logic)
            result = get_weather_info(city_name.strip(), target_hour=int(hour_val.strip()), days=1)
            #Отвечаем на сообщение пользователя, полученным результатом
            await message.reply(result)
            return

    #Если длинна более одного, и последнее является числом - выполняем алгоритм ниже
    if len(parts) > 1 and parts[-1].isdigit():
        #Возводим число в тип int
        days_count = int(parts[-1])
        #Если кол-во дней между 2 и 7 включительно, добавляем к пустой строке всю строку с городом, кроме последнего элемента и вставляем в функцию из logic.py
        if 2 <= days_count <= 7:
            city = " ".join(parts[:-1])
            result = get_weather_info(city, days=days_count)
            await message.reply(result)
            return

    #Вставляем очищенную строку, и отправляем в функцию, ответ отправляем пользователю
    result = get_weather_info(text, days=1)
    await message.reply(result)

#Запуск бота
async def main():
    print('Запуск')
    await dp.start_polling(bot)

#Если этот файл запущен не как модуль в другом файле - запуск функции main
if __name__ == "__main__":
    asyncio.run(main())
