import curses
from typing import List, Tuple
import arts
from skan import skan_window
from settings import settings_menu
from logs import log_window

# пункты внутри рамки
MENU_ITEMS: List[Tuple[str, str]] = [
    ("НАЧАТЬ", "СКАНИРОВАНИЕ"),
    ("НАСТРОЙКИ", "⚙"),
    ("ВЫХОД", "✖"),
]

LOG_COUNT = 1                # подставляй актуальное значение
IDX_LOGS = len(MENU_ITEMS)   # «виртуальный» индекс вынесенной кнопки ЛОГИ


def draw_arts(stdscr):
    for i, line in enumerate(arts.CLAMAV):
        stdscr.addstr(i + 1, 10, line)
    for i, line in enumerate(arts.ANTIVIRUS_ART):
        stdscr.addstr(i, 60, line)
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
    stdscr.addstr(y, x, "ИНФОРМАЦИЯ")
    stdscr.addstr(y + 1, x, "— готов к работе.")


def _draw_hint_box(stdscr, h, w, text):
    """Маленький бокс с подсказкой у самого низа экрана, по центру."""
    pad_x = 2
    inner_w = len(text)
    box_w = inner_w + pad_x * 2
    box_h = 3
    top = h - box_h - 1
    left = max(0, (w - box_w) // 2)

    # рамка
    _draw_box(stdscr, top, left, box_w, box_h)
    # текст
    stdscr.addstr(top + 1, left + pad_x, text)


def draw_menu(stdscr: "curses._CursesWindow", selected_idx: int) -> None:
    stdscr.clear()
    draw_arts(stdscr)

    term_h, term_w = stdscr.getmaxyx()
    h = max(30, term_h)
    w = max(65, term_w)

    box_width = 22
    box_height = len(MENU_ITEMS) + 3
    top = max(0, h // 2 - box_height // 2)
    # бокс ближе к левой половине
    left = max(0, w // 4 - box_width // 2)

    _draw_box(stdscr, top, left, box_width, box_height)

    # пункты
    y = top + 1
    x = left + 2
    inner_w = box_width - 4
    settings_row_y = None

    for idx, (label, icon) in enumerate(MENU_ITEMS):
        attr = curses.A_REVERSE if idx == selected_idx else curses.A_NORMAL
        if label == "НАЧАТЬ":
            stdscr.addstr(y, x, f" {label:<12}".ljust(inner_w), attr); y += 1
            stdscr.addstr(y, x, f" {icon:<12}".ljust(inner_w), attr);  y += 1
        else:
            stdscr.addstr(y, x, f" {label:<12} {icon}".ljust(inner_w), attr)
            if label == "НАСТРОЙКИ":
                settings_row_y = y
            y += 1

    # «ЛОГИ [n]» — на уровне строки «НАСТРОЙКИ», справа от рамки
    if settings_row_y is None:
        settings_row_y = top + 3
    logs_label = f" ЛОГИ [{LOG_COUNT}] "
    logs_x = left + box_width + 3
    logs_attr = curses.A_REVERSE if selected_idx == IDX_LOGS else curses.A_NORMAL
    stdscr.addstr(settings_row_y, logs_x, logs_label, logs_attr)

    # тонкий разделитель — только под зоной меню (короче и «легче»)
    divider_y = top + box_height + 2
    divider_left = max(2, left - 10)
    divider_len = min(box_width + 28, w - divider_left - 2)
    _draw_thin_divider(stdscr, divider_y, divider_left, divider_len)

    # инфо-блок
    _draw_info(stdscr, divider_y + 2, divider_left + 2)

    # подсказка в отдельном боксе внизу
    hint = "↑/k, ↓/j — навигация • Enter — выбрать • L — логи • Q/Esc — выход"
    _draw_hint_box(stdscr, h, w, hint)

    stdscr.refresh()


def interaction(stdscr: "curses._CursesWindow") -> None:
    curses.curs_set(0)
    stdscr.keypad(True)

    selected = 0
    draw_menu(stdscr, selected)

    while True:
        key = stdscr.getch()

        if key in (curses.KEY_UP, ord("k")):
            selected = (selected - 1) % (len(MENU_ITEMS) + 1)
        elif key in (curses.KEY_DOWN, ord("j")):
            selected = (selected + 1) % (len(MENU_ITEMS) + 1)
        elif key in (ord("l"), ord("L")):
            stdscr.clear()
            log_window(stdscr)
        elif key in (curses.KEY_ENTER, ord("\n"), ord("\r")):
            if selected == IDX_LOGS:
                stdscr.clear()
                log_window(stdscr)
            else:
                label = MENU_ITEMS[selected][0]
                stdscr.clear()
                if label == "ВЫХОД":
                    break
                elif label == "НАЧАТЬ":
                    skan_window(stdscr)
                elif label == "НАСТРОЙКИ":
                    settings_menu(stdscr)
        elif key in (27, ord("q"), ord("Q")):
            break

        draw_menu(stdscr, selected)


def main() -> None:
    curses.wrapper(interaction)


if __name__ == "__main__":
    main()
