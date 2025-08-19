import time

def skan_window(stdscr):
    skan_cycle = True
    while skan_cycle is True:
        stdscr.addstr(0, 0, f"You have chosen: SCANNING")

        # Обновление экрана
        stdscr.clrtoeol()
        stdscr.refresh()

        time.sleep(0.1)