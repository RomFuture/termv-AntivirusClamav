import curses
from typing import List, Tuple
import arts
from skan import skan_window
from settings import settings_menu
from logs import log_window

# ДЛЯ АЛИШЕРА
# TODO 1) Разобраться, в том, как работает сам код
# TODO 2) Самостоятельно начать работу над пунктом "Начать сканирование"

# (Текст, Иконка)
# ПРИМЕЧАНИЕ: БОЛЬШАЯ ПРОСЬБА НЕ ИСПОЛЬЗОВАТЬ СИМВОЛЫ ТИПА ❌ - ЛОМАЮТ ОТОБРАЖЕНИЕ

MENU_ITEMS: List[Tuple[str, str]] = [
    ("START", "SCANNING"),# ▶▶ символ «следующий»
    ("SETTINGS", "⚙"),
    ("LOGS", "▶"),
    ("EXIT", "✖"),
]

def draw_arts(stdscr):
    for item in range(len(arts.CLAMAV)):
        stdscr.addstr(item+1,10, arts.CLAMAV[item])
    for i in range(len(arts.ANTIVIRUS_ART)):
        stdscr.addstr(i + 2, 65, arts.ANTIVIRUS_ART[i])
    stdscr.refresh()


def _draw_box(stdscr, top, left, box_width, box_height):
    H, V = "-", "|"
    for x in range(box_width):
        ch = "+" if x in (0, box_width - 1) else H
        stdscr.addch(top, left + x, ch)
        stdscr.addch(top + box_height - 1, left + x, ch)
    for y in range(1, box_height - 1):
        stdscr.addch(top + y, left, V)
        stdscr.addch(top + y, left + box_width - 1, V)

def _draw_thin_divider(stdscr, y, x, length):
    """Тонкая точечная линия длиной length (короче, чем ширина экрана)."""
    pattern = (". " * (length // 2 + 2))[:length]
    stdscr.addstr(y, x, pattern)


def _draw_info(stdscr, y, x):
    stdscr.addstr(y, x, "INFORMATION — Ready to work.")
    stdscr.addstr(y + 1, x, "There are no updates. ClamAV VERSION - 0.001")


def _draw_hint_box(stdscr, h, w, text):
    """Маленький бокс с подсказкой у самого низа экрана, по центру."""
    pad_x = 2
    inner_w = len(text)
    box_w = inner_w + pad_x * 2
    box_h = 3
    top = h - box_h - 1
    left = 26

    # рамка
    _draw_box(stdscr, top, left, box_w, box_h)
    # текст
    stdscr.addstr(top + 1, left + pad_x, text)

def draw_menu(stdscr: "curses._CursesWindow", selected_idx: int) -> None:
    """Отрисовать рамку и пункты меню."""
    stdscr.clear()
    draw_arts(stdscr)
    # Размещение на экране
    h = 30
    w = 65

    # Геометрия рамки
    box_width = 20
    box_height = len(MENU_ITEMS) + 3  # по строке сверху и снизу для рамки
    top = max(0, h // 2 - box_height // 2)
    left = max(0, w // 2 - box_width // 2)

    # ЗНАКИ ДЛЯ ОТРИСОВКИ РАМКИ
    H_CHAR = "-"  # горизонтальный штрих
    V_CHAR = "|"  # вертикальный штрих

    # Отрисовка краёв работает по принципу: есть цикл for, а в нём условие char:
    # Если край бокса, то сделай +, если нет поставь нужный знак - или |

    # Верхний/нижний края
    for x in range(box_width):
        char = "+" if x == 0 or x == box_width-1 else H_CHAR
        # рисует линию сверху и снизу
        stdscr.addch(top, left + x, char)
        stdscr.addch(top + box_height - 1, left + x, char)

    # Отрисовка боковые краёв
    for y in range(1, box_height - 1):
        char = V_CHAR
        stdscr.addch(top + y, left, char)
        stdscr.addch(top + y, left + box_width -1, char)

    # Пункты меню (конечно, это ёбанный колхоз, но зато работает)
    # Работает по принципу - перебирает всё в dict MENU_ITEMS и отрисовывает их вместе с иконками (смайлами)
    y = top + 1
    x = left + 2
    inner_w = box_width - 4

    for idx, (label, icon) in enumerate(MENU_ITEMS):
        attr = curses.A_REVERSE if idx == selected_idx else curses.A_NORMAL
        if label != "START":
            text = f" {label:<5} {icon} " # выравниваем подпись
        else:
            text1 = f" {label:<5}" # выравниваем подпись
            text = f" {icon:<5}"
            stdscr.addstr(y, x, text1.ljust(inner_w), attr)
            y += 1
        stdscr.addstr(y, x, text.ljust(inner_w), attr)
        y += 1

    # тонкий разделитель — только под зоной меню (короче и «легче»)
    divider_y = top + box_height + 2
    divider_left = max(2, left - 10)
    divider_len = min(box_width + 28, w - divider_left - 2)
    _draw_thin_divider(stdscr, divider_y, divider_left, divider_len)

    # инфо-блок
    _draw_info(stdscr, divider_y + 2, divider_left + 2)

    # подсказка в отдельном боксе внизу
    hint = "↑/k, ↓/j — navigation • Enter — select • L — logs • Q/Esc — exit"
    _draw_hint_box(stdscr, h, w, hint)

    stdscr.refresh()

# ГЛАВНЫЙ ЦИКЛ - ЛОВИМ ДЕЙСТВИЯ ПОЛЬЗОВАТЕЛЯ
def interaction(stdscr: "curses._CursesWindow") -> None:
    curses.curs_set(0)  # убираем курсор
    stdscr.keypad(True)

    selected = 0
    draw_menu(stdscr, selected)
    draw_arts(stdscr)

    while True:
        key = stdscr.getch()

        if key in (curses.KEY_UP, ord("k")):
            selected = (selected - 1) % len(MENU_ITEMS)
        elif key in (curses.KEY_DOWN, ord("j")):
            selected = (selected + 1) % len(MENU_ITEMS)
        elif key in (curses.KEY_ENTER, ord("\n"), ord("\r")):
            label = MENU_ITEMS[selected][0]
            stdscr.clear()
            if label == "EXIT":
                break
            elif label == "START":
                skan_window(stdscr)
            elif label == "SETTINGS":
                settings_menu(stdscr)
            elif label == "LOGS":
                log_window(stdscr)

        elif key in (27, ord("q")):
            break

        draw_menu(stdscr, selected)

def main() -> None:
    """Точка входа."""
    curses.wrapper(interaction)


if __name__ == "__main__":
    main()
