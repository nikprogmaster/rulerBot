import telebot
from PhraseSender import PhraseSender
from threading import Thread
from time import sleep
import keyboard

BOT_TOKEN = '2049393246:AAEn8VcXip1p0O-k8sgYMakhFJue_FGEcwo'
BOT_INTERVAL = 3
BOT_TIMEOUT = 30
MAX_MAINTAINERS = 5

bot = telebot.TeleBot(BOT_TOKEN)
maintainers = []
all_phrases = []
active_maintainers = {}


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


def resetAllSessions():
    global bot
    for m in active_maintainers.values():
        m.is_game_started = False
    active_maintainers.clear()
    f = open('maintainers_ids.txt', 'r')
    for idenf in f:
        idenf.rstrip()
        bot.send_message(idenf, "Бот обновился, теперь он немного лучше", reply_markup=keyboard.get_begining_keyboard())
    f.close()


def bot_polling():
    global bot
    print("Starting bot polling now")
    init()
    resetAllSessions()
    while True:
        try:
            print("New bot instance started")
            init()
            bot_actions()
            bot.polling(none_stop=True, interval=BOT_INTERVAL, timeout=BOT_TIMEOUT)
        except Exception as ex:
            print("Bot polling failed, restarting in {}sec. Error:\n{}".format(BOT_TIMEOUT, ex))
            bot.stop_polling()
            sleep(BOT_TIMEOUT)
        else:
            bot.stop_polling()
            print("Bot polling loop finished")
            break


def save_maintainer_id(identificator):
    f = open('maintainers_ids.txt', 'w')
    f.write(str(identificator) + '\n')
    f.close()


def bot_actions():
    @bot.message_handler(commands=['start'], content_types=['text'])
    def send_welcome(message):
        if message.chat.username in maintainers:
            bot.send_message(message.chat.id, "Привет, " + message.chat.first_name + "!",
                             reply_markup=keyboard.get_begining_keyboard())
            save_maintainer_id(message.chat.id)
        else:
            user_markup = telebot.types.ReplyKeyboardMarkup(True)
            user_markup.row(keyboard.start_game)
            bot.send_message(message.chat.id, "Добро пожаловать!", reply_markup=user_markup)

    @bot.message_handler(content_types=['text'])
    def bot_managering(message):
        if message.chat.type == 'private':
            maintainer = active_maintainers.get(message.chat.username)
            if message.text == keyboard.start_new_game:
                if maintainer is not None and maintainer.is_game_started:
                    bot.send_message(message.chat.id, "Ты уже играешь!", reply_markup=keyboard.get_before_game_keyboard())
                elif len(active_maintainers) >= MAX_MAINTAINERS:
                    bot.send_message(message.chat.id,
                                     "Привет! Прости, сейчас много людей пользуется ботом. Подожди немного")
                else:
                    maintainer = PhraseSender(maintainers.index(message.chat.username),
                                              message.chat.username)
                    active_maintainers[message.chat.username] = maintainer
                    maintainer.is_game_started = True
                    bot.send_message(message.chat.id, 'Введите размер группы. Ее размер должен быть от 2 до 20',
                                     reply_markup=keyboard.get_before_game_keyboard())
            elif maintainer is not None and message.text == keyboard.continue_game:
                if maintainer.group_number == 0:
                    bot.send_message(message.chat.id, 'Вы не ввели размер группы!',
                                     reply_markup=keyboard.get_before_game_keyboard())
                else:
                    bot.send_message(message.chat.id,
                                     'Новая игра! Ваш id = ' + str(maintainer.uniq_id) + '. Сообщите его участникам',
                                     reply_markup=keyboard.get_pre_start_keyboard())
            elif message.text == keyboard.participants_number:
                bot.send_message(message.chat.id,
                                 'Сейчас ' + str(len(maintainer.participants)) + maintainer.get_correct_ending(),
                                 reply_markup=keyboard.get_pre_start_keyboard())
            elif message.text == keyboard.start_playing:
                bot.send_message(message.chat.id, 'Игра началась', reply_markup=keyboard.get_game_keyboard())
                Thread(target=maintainer.give_phrases(all_phrases, bot)).start()
            elif message.text == keyboard.start_game:
                bot.send_message(message.chat.id, 'Введите id игры')
            elif message.text == exit and maintainer is not None:
                maintainer.is_game_started = False
                active_maintainers.pop(maintainer.maintainer_username)
                bot.send_message(message.chat.id, 'Игра окончена', reply_markup=keyboard.get_begining_keyboard())
            elif message.text == keyboard.back:
                bot.send_message(message.chat.id, 'Введите размер группы. Ее размер должен быть от 2 до 20',
                                 reply_markup=keyboard.get_before_game_keyboard())
            elif message.text.isdigit():
                if maintainer is not None and message.chat.username == maintainer.maintainer_username:
                    if int(message.text) in range(2, 21):
                        maintainer.group_number = int(message.text)
                        print(str(maintainer.group_number))
                        bot.send_message(message.chat.id,
                                         'Отлично! Размер группы ' + message.text + '. Максимальное количество участников для такого размера - ' + str(
                                             20 * int(
                                                 message.text)) + '. Если их будет больше, бот автоматически увеличит размер группы',
                                         reply_markup=keyboard.get_before_game_keyboard_with_back())
                    else:
                        bot.send_message(message.chat.id, 'Введите размер группы. Ее размер должен быть от 2 до 20',
                                         reply_markup=keyboard.get_before_game_keyboard())
                else:
                    maintainer = find_maintainer_by_id(int(message.text))
                    if maintainer is not None and maintainer.is_game_started is True:
                        maintainer.add_participant(message.chat.id)
                        bot.send_message(message.chat.id, 'Поздравляю, ты в игре!')
                    else:
                        bot.send_message(message.chat.id, 'Прости, игра еще не началась :(')


bot_polling()
