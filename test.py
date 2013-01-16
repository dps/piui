import random
import time
from rpi import AndroidPiUi

def main():
    ui = AndroidPiUi()

    con = ui.console()
    i = 0
    while True:
        time.sleep(int(random.uniform(0, 2)))
        ui.print_line("foo " + str(i))
        i = i + 1
    ui.done()

if __name__ == '__main__':
    main()