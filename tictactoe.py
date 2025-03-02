# Игра крестики-нолики
import random

# Задаем конструкцию поля, пустое по-умолчанию
field = [['-'] * 3 for _ in range(3)]
str_format = 'используйте цифры от 1 до 3 разделенные пробелом в формате: строка столбец'
str_info = 'Введенный формат хода некорректен'
str_end = '\033[0m'

# Функционал печати поля
def print_matrix():
    l = []; print('')
    # Добавляем нумерацию колонок и столбцов
    for i in range(len(field)):
        lp = field[i].copy()
        lp.insert(0, str(i + 1))
        l.append(lp)
    l.insert(0, [' ', '1', '2', '3'])
    [print(*r) for r in zip(*l)]

# Декоратор, проверяющий правильность хода
def step_is_valid(p_func):
    def wrapper(p_player):
        while True:
            try:
                col, row = map(int, input(f'Ход игрока "{p_player}": ').split())
                col, row = col - 1, row - 1
            except ValueError:
                print(f'\033[31m{str_info}, {str_format}{str_end}')
                print_matrix()
                continue
            if 0 <= col <= 2 and 0 <= row <= 2:
                if field[row][col] == '-':
                    p_func(p_player = p_player, p_row = row, p_col = col)
                    break
                else:
                    print(f'\033[31mВыберете ход повторно, клетка ({col + 1},{row + 1}) уже занята игроком "{field[row][col] }"{str_end}')
                    print_matrix()
            else:
                print(f'\033[31m{str_info}, значение хода от 1 до 3 вкл.{str_end}')
                print_matrix()
    return wrapper

# Пользовательский ход и проверка завершения игры
@step_is_valid
def user_moves(p_player: str, p_row: int, p_col: int):
    field[p_row][p_col] = p_player
    print_matrix()
    if all([field[p_row][i] == p_player for i in range(3)]) or \
        all([field[i][p_col] == p_player for i in range(3)]) or \
        all([field[i][i] == p_player for i in range(3)]) or \
        all([field[2 - i][i] == p_player for i in range(3)]):
        print(f'\n\033[32mИгра закончена: победа игрока "{p_player}"!{str_end}')
        exit()
    elif not [i for i in field if '-' in i]:
        print(f'\n\033[32mИгра закончена: ничья!{str_end}')
        exit()

# Начальное отражение игрового поля
print_matrix()
print(f'\n\033[33mДобро пожаловать в игру крестики-нолики!\n'
      f'При вводе хода {str_format}{str_end}')
player = random.choices('ox')[0] # Выбор первого хода
# Начало игры
while True:
    user_moves(p_player = player)
    player = 'o' if player == 'x' else 'x'