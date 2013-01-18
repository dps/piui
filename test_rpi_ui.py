import os
import random
import time
from piui import AndroidPiUi

current_dir = os.path.dirname(os.path.abspath(__file__))

def onupclick():
    title.set_text("Up")
    print "Up"

def ondownclick():
    title.set_text("Down")
    print "Down"

def onhelloclick():
    print "onstartclick"
    title.set_text("Hello " + txt.get_text())
    print "Start"

def onpicclick():
    img.set_src("sunset2.png")

def onconsoleclick():
    con = ui.console()
    con.print_line("Hello Console!")

title = None
txt = None
img = None
ui = None
def main():
    global title, txt, img, ui
    ui = AndroidPiUi(img_dir=os.path.join(current_dir, 'imgs'))

    con = ui.console()
    i = 0
    while i < 5:
        time.sleep(int(random.uniform(0, 2)))
        ui.print_line("foo " + str(i))
        i = i + 1
    page = ui.new_ui_page(title="AndroidPiUi")
    title = page.add_textbox("Hello, World", "h1")
    page.start_span()
    txt = page.add_input("text", "Name")
    button = page.add_button("Say Hello", onhelloclick)
    button2 = page.add_button("Change The Picture", onpicclick)
    page.end_span()
    txtbox = page.add_textbox("Lorem ipsum dolor sit amet, consectetur adipiscing elit. Etiam tortor leo, posuere id mattis ut, sollicitudin vitae massa. Nulla lacus metus, aliquam vel dapibus ac, vehicula sit amet nisi. In vel enim leo. Ut tellus sem, blandit et porttitor in, rhoncus eget mi. Aliquam tristique, sem eu tincidunt rhoncus, libero mi placerat libero, et tincidunt nisi eros eget lectus. Aliquam commodo nulla nec diam hendrerit molestie. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia Curae;")
    plus = page.add_button("&uarr;", onupclick)
    minus = page.add_button("&darr;", ondownclick)
    cons = page.add_button("Console", onconsoleclick)
    img = page.add_image("sunset.png")
    time.sleep(5)
    title.set_text("Foo the bar baz.")
    ui.done()

if __name__ == '__main__':
    main()