from sqlalchemy.orm import Session
import game
import random
from telebot.types import Message
from telebot import TeleBot

from core.db import get_db
from core.db_helper import update_user_stats

queueChatIds: list[int] = []
activeGames: list[game.Game] = []

# Запрос на старт игры
def processANewGameRequest(b: TeleBot, message: Message):
    chatId = message.chat.id
    if getCurrentPlayerGame(chatId):  # Уже в игре
        b.send_message(chatId, 'Вы уже в игре!')
        return
    if chatId in queueChatIds:  # Уже ожидает игры
        b.send_message(chatId, 'Вы уже в очереди ожидания!')
        return

    if len(queueChatIds) == 0:  # Добавление в список ожидания
        queueChatIds.append(chatId)
        b.send_message(chatId, 'Вы добавлены в очередь ожидания\nДля отмены напишите /leavegame')
        return

    otherPlayerID = queueChatIds[0]
    queueChatIds.pop(0)
    startNewGame(b, chatId, otherPlayerID)

# Техническая реализация старта игры
def startNewGame(b: TeleBot, id1, id2):
    newGame = game.Game()

    data1 = game.PlayerData()
    data1.pId = id1
    data1.markedCells = []

    data2 = game.PlayerData()
    data2.pId = id2
    data2.markedCells = []

    if random.randint(0, 1):
        data1.sign = 'X'
        data2.sign = 'O'
        newGame.p1TurnNow = True
    else:
        data1.sign = 'O'
        data2.sign = 'X'
        newGame.p1TurnNow = False

    newGame.p1 = data1
    newGame.p2 = data2

    activeGames.append(newGame)
    for chatId in [data1.pId, data2.pId]:
        b.send_message(chatId, 'Игра начинается!')

    displayStateAskAndStopAtWin(b, newGame)


def processAMoveRequest(b: TeleBot, message: Message, text=None):
    chatId = message.chat.id
    game = getCurrentPlayerGame(chatId)
    if not game:
        b.send_message(chatId, 'Сначала присоединитесь к игре, написав /joingame')
        return

    if chatId == game.p2.pId and game.p1TurnNow or chatId == game.p1.pId and not game.p1TurnNow:
        b.send_message(chatId, 'Сейчас не ваш ход!')
        return

    if not text:
        text = message.text
    text = text.replace(' ', '')
    if len(text) != 2:
        b.send_message(chatId, 'Введите коодинаты в формате двух чисел, например "1 3"')
        return

    try:
        coord1 = int(text[0])
        coord2 = int(text[1])
    except ValueError:
        b.send_message(chatId, 'Координаты должны быть числами, например "1 3"')
        return

    performNextMovement(b, game, (coord1 - 1, coord2 - 1))

# Техническая реализация совершения хода
def performNextMovement(b: TeleBot, game: game.Game, coords):
    p = game.p2
    otherP = game.p1
    if game.p1TurnNow:  # Выяснение, чей сейчас ход
        p = game.p1
        otherP = game.p2

    if coords[0] < 0 or coords[0] > 2 or coords[1] < 0 or coords[1] > 2:
        b.send_message(p.pId, 'Координаты должны быть в диапазоне [1-3]!')
        return

    if coords in p.markedCells:
        b.send_message(p.pId, 'Вы уже заняли эту клетку!')
        return

    if coords in otherP.markedCells:
        b.send_message(p.pId, 'Ваш противник уже занял эту клетку!')
        return

    p.markedCells.append(coords)
    game.p1TurnNow = not game.p1TurnNow

    maybeWinner = game.checkSomeoneWon()
    maybeADraw = game.checkADraw()
    displayStateAskAndStopAtWin(b, game, winner=maybeWinner, draw=maybeADraw)



# Запрос покинуть игру
def processLeaveGameRequest(b: TeleBot, message: Message, db: Session = None):
    if db is None:
        db = next(get_db())  # Получаем сессию, если она не была передана

    chatId = message.chat.id
    game = getCurrentPlayerGame(chatId)  # Получаем текущую игру игрока
    if not game:
        if chatId in queueChatIds:  # Игрок в очереди
            queueChatIds.remove(chatId)  # Убираем игрока из очереди ожидания
            b.send_message(chatId, 'Вы успешно покинули очередь ожидания игры')
            return
        else:
            b.send_message(chatId, 'Вы уже не в игре!')  # Игрок не в игре
            return

    # Если игра есть, обрабатываем выход
    otherP = game.p1
    if otherP.pId == chatId:  # Определяем другого игрока, если текущий игрок — первый
        otherP = game.p2

    # Обновление статистики пользователей
    update_user_stats(chatId, 0, 1, 0, db)  # Текущий игрок проиграл
    update_user_stats(otherP.pId, 1, 0, 0, db)  # Противник выиграл

    # Отправляем сообщение об окончании игры
    b.send_message(chatId, 'Игра преждевременно завершена')
    b.send_message(otherP.pId, 'Противник преждевременно завершил игру')
    activeGames.remove(game)  # Удаляем игру из активных

# Вспомогательная функция получения текущей игры для пользователя, если такая есть
def getCurrentPlayerGame(chatId):
    for g in activeGames:
        if g.p1.pId == chatId or g.p2.pId == chatId:
            return g

# Вспомогательная функция отправки сообщения после каждого хода
def displayStateAskAndStopAtWin(b: TeleBot, game: game.Game, winner: game.PlayerData = None, draw: bool = None):
    displayCurrentStateForPlayer(b, game, game.p1, winner, draw)
    displayCurrentStateForPlayer(b, game, game.p2, winner, draw)
    if winner or draw:
        activeGames.remove(game)

# Вспомогательная функция отправки сообщения после каждого хода для конкретного игрока
def displayCurrentStateForPlayer(b: TeleBot, game: game.Game, p: game.PlayerData, winner: game.PlayerData = None, draw: bool = None):
    s = 'Игровое поле:\n\n' + game.getVisualBoardState() + '\n\n'
    if not winner and not draw:
        s += 'Ваш символ: ' + p.sign + '\n'
        if game.p1TurnNow and p == game.p1 or not game.p1TurnNow and p == game.p2:
            s += 'Введите свой следующий шаг (два числа - номер строки и номер столбца):'
        else:
            s += 'Ожидание хода противника...'
    elif winner:
        if p == winner:
            s += 'Вы победили! 🎉'
        else:
            s += 'Вы проиграли'
    elif draw:
        s += 'Ничья!\nИгра завершена'
    b.send_message(p.pId, s)
