import telebot

import game_manager
from auth import token
from telebot.types import Message

# Авторизация и получение переменной для работы с ботом
bot = telebot.TeleBot(token.getToken())

# Вынесенный из функции для читаемости текст одной из команд
usageInstruction = "Инструкция по использованию:\n" + \
                "Для участия в игре используйте команду /joingame и подождите второго игрока.\n" + \
                "Для отмены или выхода из игры используйте команду /leavegame.\n" + \
                "Удачной игры!"

# Обработчик команд "start" и "help" в приватных чатах и группах
@bot.message_handler(commands=['start', 'help'], chat_types=['private', 'group'])
def send_welcome(message):
    bot.reply_to(message, usageInstruction)

# Обработчик команды "joingame" в приватных чатах и группах
@bot.message_handler(commands=['joingame'], chat_types=['private', 'group'])
def send_welcome(message: Message):
    game_manager.processANewGameRequest(bot, message)

# Обработчик команды "leavegame" в приватных чатах и группах
@bot.message_handler(commands=['leavegame'], chat_types=['private', 'group'])
def send_welcome(message: Message):
    game_manager.processLeaveGameRequest(bot, message)

# Обработчик остальных сообщений в приватных чатах (и команд в группах)
@bot.message_handler()
def echo_all(message: Message):
    if message.text.startswith('/t '): # Для доступа в группах по такой команде, по большей части сделано для тестирования
        game_manager.processAMoveRequest(bot, message, text=message.text[3:])
    else:
        game_manager.processAMoveRequest(bot, message)


# (Конец определённых повыше функций, начало основной части программы)

# Установка легкодоступных команд в меню "слева"
bot.set_my_commands(commands=[
    telebot.types.BotCommand(command='joingame', description='Присоединиться к игре'),
    telebot.types.BotCommand(command='leavegame', description='Покинуть игру'),
    telebot.types.BotCommand(command='help', description='Помощь')
])
# Запуск получения новых сообщений
print('Бот запущен!')
bot.infinity_polling()
