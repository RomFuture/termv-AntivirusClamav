import time

def settings_menu(stdscr):
    skan_cycle = True
    while skan_cycle is True:
        stdscr.addstr(0, 0, "You have chosen: settings")

        # Обновление экрана
        stdscr.clrtoeol()
        stdscr.refresh()

        time.sleep(0.1)

