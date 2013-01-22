import os
import random
import time
from piui import AndroidPiUi

current_dir = os.path.dirname(os.path.abspath(__file__))


class DemoPiUi(object):

    def __init__(self):
        self.title = None
        self.txt = None
        self.img = None
        self.ui = AndroidPiUi(img_dir=os.path.join(current_dir, 'imgs'))
        self.src = "sunset.png"

    def main(self):
        self.page = self.ui.new_ui_page(title="AndroidPiUi")
        self.title = self.page.add_textbox("Hello, World", "h1")
        self.page.start_span()
        self.txt = self.page.add_input("text", "Name")
        button = self.page.add_button("Say Hello", self.onhelloclick)
        button2 = self.page.add_button("Change The Picture", self.onpicclick)
        self.page.end_span()
        txtbox = self.page.add_textbox("Lorem ipsum dolor sit amet, consectetur adipiscing elit.")
        plus = self.page.add_button("&uarr;", self.onupclick)
        minus = self.page.add_button("&darr;", self.ondownclick)
        cons = self.page.add_button("Console", self.onconsoleclick)
        self.page.add_element("br")
        self.img = self.page.add_image("sunset.png")
        self.list = self.page.add_list()
        self.list.add_item("List item 1", chevron=False, toggle=True, ontoggle=self.ontoggle)
        self.list.add_item("List item 2", chevron=True, toggle=False)
        time.sleep(5)
        self.title.set_text("Hello Again.")
        self.ui.done()

    def onupclick(self):
        self.title.set_text("Up")
        print "Up"

    def ondownclick(self):
        self.title.set_text("Down")
        print "Down"

    def onhelloclick(self):
        print "onstartclick"
        self.title.set_text("Hello " + self.txt.get_text())
        print "Start"

    def onpicclick(self):
        if self.src == "sunset.png":
          self.img.set_src("sunset2.png")
          self.src = "sunset2.png"
        else:
          self.img.set_src("sunset.png")
          self.src = "sunset.png"

    def onconsoleclick(self):
        con = self.ui.console()
        con.print_line("Hello Console!")

    def ontoggle(self, value):
        self.title.set_text("Toggled! " + str(value))

def main():
  piui = DemoPiUi()
  piui.main()

if __name__ == '__main__':
    main()