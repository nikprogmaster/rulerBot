import telebot
import random
from telebot import types

bot = telebot.TeleBot('1944148983:AAHF2wKQ95gCOF1dGDzRVugGmesZDXM1dqE')
maintainer = ""
is_game_started = False
all_phrases = []


def get_begining_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    key_start_game = types.InlineKeyboardButton(text='Начать игру!', callback_data='start_game')
    keyboard.add(key_start_game)
    return keyboard


def get_pre_start_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    participants_number = types.InlineKeyboardButton("Количество участников", callback_data="parts_number")
    start_playing = types.InlineKeyboardButton("Старт", callback_data="start_playing")
    keyboard.add(participants_number)
    keyboard.add(start_playing)
    return keyboard


def get_game_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    exit = types.InlineKeyboardButton("Завершить игру", callback_data="exit")
    keyboard.add(exit)
    return keyboard


def init():
    global maintainer
    f = open('maintainer.txt', 'r')
    maintainer = f.read()
    maintainer.rstrip()
    f.close()
    global all_phrases
    f = open('phrases.txt', 'r', encoding="utf-8")
    for line in f:
        all_phrases.append(line)
    f.close()


def read_participants():
    participants = []
    f = open('participants.txt', 'r')
    for participant in f:
        participants.append(participant)
    f.close()
    participants = [line.rstrip() for line in participants]
    return participants


def give_phrases(parts):
    p = parts.copy()
    ph = all_phrases.copy()
    index = len(p)
    while index > 0:
        parts_group = []
        step = 4
        if len(p) < 4:
            step = len(p)
        for i in range(step):
            parts_group.append(get_random_participant(p))
        rp = random.randrange(0, len(ph))
        phrase = ph[rp]
        ph.remove(ph[rp])
        index -= step
        for i in parts_group:
            bot.send_message(i, phrase)


def get_random_participant(parts):
    index = random.randrange(0, len(parts))
    participant = parts[index]
    parts.remove(parts[index])
    return participant


@bot.message_handler(commands=['start'], content_types=['text'])
def send_welcome(message):
    if message.chat.username == maintainer:
        bot.send_message(message.chat.id, "Привет, хозяин!", reply_markup=get_begining_keyboard())
    else:
        bot.send_message(message.chat.id, "Поздравляю, ты в игре!")
        parts = read_participants()
        if str(message.chat.id) not in parts:
            f = open('participants.txt', 'a')
            f.write(str(message.chat.id) + '\n')
            f.close()


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    global is_game_started
    if call.data == "start_game":
        if not is_game_started:
            f = open('participants.txt', 'w')
            f.close()
            is_game_started = True
            keyboard = get_pre_start_keyboard()
            bot.send_message(call.message.chat.id, "Новая игра! Собираем участников...", reply_markup=keyboard)
    elif call.data == "parts_number":
        parts = read_participants()
        keybord = get_pre_start_keyboard()
        bot.send_message(call.message.chat.id, 'Сейчас ' + str(len(parts)) + ' участников', reply_markup=keybord)
    elif call.data == "start_playing":
        parts = read_participants()
        keyboard = get_game_keyboard()
        bot.send_message(call.message.chat.id, 'Игра началась', reply_markup=keyboard)
        give_phrases(parts)
    elif call.data == "exit":
        is_game_started = False
        keyboard = get_begining_keyboard()
        bot.send_message(call.message.chat.id, 'Игра окончена', reply_markup=keyboard)


init()

print('Bot is working')
bot.polling(non_stop=True, interval=1)
