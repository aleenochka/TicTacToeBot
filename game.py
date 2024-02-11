# Класс данных об одном из игроков
class PlayerData:
    pId: int
    sign: str
    markedCells: list[tuple[int, int]]

# Класс данных о всей игре
class Game:
    p1: PlayerData
    p2: PlayerData
    p1TurnNow: bool

    # Функция печати игрового поля в текстовом виде
    def getVisualBoardState(self):
        s = ''
        for i in range(3):
            for j in range(3):
                if (i, j) in self.p1.markedCells:
                    s += '  ' + self.p1.sign + '  '
                elif (i, j) in self.p2.markedCells:
                    s += '  ' + self.p2.sign + '  '
                else:
                    s += '      '

                if j < 2:
                    s += '|'
            if i < 2:
                s += '\n——————\n'
        return s

    # Функция для проверки победы и определения победителя
    def checkSomeoneWon(self):
        winCombinations = [
            [(0, 0), (0, 1), (0, 2)],
            [(1, 0), (1, 1), (1, 2)],
            [(2, 0), (2, 1), (2, 2)],
            [(0, 0), (1, 0), (2, 0)],
            [(0, 1), (1, 1), (2, 1)],
            [(0, 2), (1, 2), (2, 2)],
            [(1, 1), (2, 2), (3, 3)],
            [(1, 3), (2, 2), (3, 1)]
        ]

        for comb in winCombinations:
            if set(comb).issubset(set(self.p1.markedCells)):
                return self.p1
            if set(comb).issubset(set(self.p2.markedCells)):
                return self.p2

    def checkADraw(self):
        for i in range(3):
            for j in range(3):
                if not (i, j) in self.p1.markedCells and not (i, j) in self.p2.markedCells:
                    return False
        return True
