#Меню reply keyboard, вы можете изменить или добавить свои вариации кнопок
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_menu():
    kb = [
        [KeyboardButton(text="Москва"), KeyboardButton(text="Улан-Удэ")],
        [KeyboardButton(text="Краснодар"), KeyboardButton(text="Санкт-Петербург")],
        [KeyboardButton(text="Настройки")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, input_field_placeholder="Введите свой город")

def help_menu():
    kb = [
        [KeyboardButton(text="Написать в поддержку!"), KeyboardButton(text="Выбрать время")],
        [KeyboardButton(text="Назад")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, input_field_placeholder="Введите свой город")

def hours_menu():
    kb = [
        [KeyboardButton(text="На несколько дней вперед")],
        [KeyboardButton(text="Назад в настройки")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, input_field_placeholder="Введите свой город, введите час")

def days_menu():
    kb = [[KeyboardButton(text="Назад в выбор времени")]]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)