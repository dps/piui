import random
import time
from rpi import AndroidPiUi

def onupclick():
    print "Up"

def ondownclick():
    print "Down"

def onstartclick():
    print "Start"

def main():
    ui = AndroidPiUi()

    con = ui.console()
    i = 0
    while i < 5:
        time.sleep(int(random.uniform(0, 2)))
        ui.print_line("foo " + str(i))
        i = i + 1
    page = ui.new_ui_page(title="AndroidPiUi")
    title = page.add_textbox("Hello, World", "h1")
    txtbox = page.add_textbox("Lorem ipsum dolor sit amet, consectetur adipiscing elit. Etiam tortor leo, posuere id mattis ut, sollicitudin vitae massa. Nulla lacus metus, aliquam vel dapibus ac, vehicula sit amet nisi. In vel enim leo. Ut tellus sem, blandit et porttitor in, rhoncus eget mi. Aliquam tristique, sem eu tincidunt rhoncus, libero mi placerat libero, et tincidunt nisi eros eget lectus. Aliquam commodo nulla nec diam hendrerit molestie. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia Curae;")
    page.start_span()
    plus = page.add_button("&uarr;", onupclick)
    minus = page.add_button("&darr;", ondownclick)
    button = page.add_button("Start", onstartclick)
    page.end_span()
    time.sleep(5)
    title.set_text("Foo the bar baz.")
    ui.done()

if __name__ == '__main__':
    main()