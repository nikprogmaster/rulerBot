from telebot import types

start_new_game = 'Начать новую игру'
continue_game = 'Продолжить'
back = 'Назад'
start_game = 'Начать игру'
participants_number = 'Количество участников'
start_playing = 'Старт'
exit = 'Завершить игру'


def get_begining_keyboard():
    keyboard = types.ReplyKeyboardMarkup(True, True)
    keyboard.row(start_new_game)
    return keyboard


def get_pre_start_keyboard():
    keyboard = types.ReplyKeyboardMarkup(True, True)
    keyboard.row(participants_number, start_playing)
    return keyboard


def get_game_keyboard():
    keyboard = types.ReplyKeyboardMarkup(True, True)
    keyboard.row(exit)
    return keyboard


def get_before_game_keyboard():
    keyboard = types.ReplyKeyboardMarkup(True, True)
    keyboard.row(continue_game)
    return keyboard


def get_before_game_keyboard_with_back():
    keyboard = types.ReplyKeyboardMarkup(True, True)
    keyboard.row(continue_game, back)
    return keyboard

