import telebot
from PhraseSender import PhraseSender
from telebot import types
from threading import Thread

bot = telebot.TeleBot('2049393246:AAEn8VcXip1p0O-k8sgYMakhFJue_FGEcwo')
maintainers = []
all_phrases = []
active_maintainers = {}

max_maintainers = 5

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


def init():
    global maintainers
    f = open('maintainers.txt', 'r')
    for line in f:
        maintainers.append(line)
    maintainers = [line.rstrip() for line in maintainers]
    f.close()
    global all_phrases
    f = open('phrases.txt', 'r', encoding="utf-8")
    for line in f:
        all_phrases.append(line)
    f.close()


def find_maintainer_by_id(identificator):
    for m in active_maintainers.values():
        if m.uniq_id == identificator:
            return m


@bot.message_handler(commands=['start'], content_types=['text'])
def send_welcome(message):
    if message.chat.username in maintainers:
        bot.send_message(message.chat.id, "Привет, " + message.chat.first_name + "!", reply_markup=get_begining_keyboard())
    else:
        user_markup = telebot.types.ReplyKeyboardMarkup(True)
        user_markup.row(start_game)
        bot.send_message(message.chat.id, "Добро пожаловать!", reply_markup=user_markup)


@bot.message_handler(content_types=['text'])
def bot_managering(message):
    if message.chat.type == 'private':
        maintainer = active_maintainers.get(message.chat.username)
        if message.text == start_new_game:
            if maintainer is not None and maintainer.is_game_started:
                bot.send_message(message.chat.id, "Ты уже играешь!", reply_markup=get_before_game_keyboard())
            elif len(active_maintainers) >= max_maintainers:
                bot.send_message(message.chat.id,
                                 "Привет! Прости, сейчас много людей пользуется ботом. Подожди немного")
            else:
                maintainer = PhraseSender(maintainers.index(message.chat.username),
                                          message.chat.username)
                active_maintainers[message.chat.username] = maintainer
                maintainer.is_game_started = True
                bot.send_message(message.chat.id, 'Введите размер группы. Ее размер должен быть от 2 до 20',
                                 reply_markup=get_before_game_keyboard())
        elif maintainer is not None and message.text == continue_game:
            if maintainer.group_number == 0:
                bot.send_message(message.chat.id, 'Вы не ввели размер группы!', reply_markup=get_before_game_keyboard())
            else:
                bot.send_message(message.chat.id,
                                 'Новая игра! Ваш id = ' + str(maintainer.uniq_id) + '. Сообщите его участникам',
                                 reply_markup=get_pre_start_keyboard())
        elif message.text == participants_number:
            bot.send_message(message.chat.id, 'Сейчас ' + str(len(maintainer.participants)) + maintainer.get_correct_ending(),
                             reply_markup=get_pre_start_keyboard())
        elif message.text == start_playing:
            bot.send_message(message.chat.id, 'Игра началась', reply_markup=get_game_keyboard())
            Thread(target=maintainer.give_phrases(all_phrases, bot)).start()
        elif message.text == start_game:
            bot.send_message(message.chat.id, 'Введите id игры')
        elif message.text == exit and maintainer is not None:
            maintainer.is_game_started = False
            active_maintainers.pop(maintainer.maintainer_username)
            bot.send_message(message.chat.id, 'Игра окончена', reply_markup=get_begining_keyboard())
        elif message.text == back:
            bot.send_message(message.chat.id, 'Введите размер группы. Ее размер должен быть от 2 до 20',
                             reply_markup=get_before_game_keyboard())
        elif message.text.isdigit():
            if maintainer is not None and message.chat.username == maintainer.maintainer_username:
                if int(message.text) in range(2, 21):
                    maintainer.group_number = int(message.text)
                    bot.send_message(message.chat.id,
                                     'Отлично! Размер группы ' + message.text + '. Максимальное количество участников для такого размера - ' + str(
                                         20 * int(message.text)) + '. Если их будет больше, бот автоматически увеличит размер группы', reply_markup=get_before_game_keyboard_with_back())
                else:
                    bot.send_message(message.chat.id, 'Введите размер группы. Ее размер должен быть от 2 до 20',
                                     reply_markup=get_before_game_keyboard())
            else:
                maintainer = find_maintainer_by_id(int(message.text))
                if maintainer is not None and maintainer.is_game_started is True:
                    maintainer.add_participant(message.chat.id)
                    bot.send_message(message.chat.id, 'Поздравляю, ты в игре!')
                else:
                    bot.send_message(message.chat.id, 'Прости, игра еще не началась :(')


init()

print('Bot is working')
bot.polling(non_stop=True, interval=1)
