import cherrypy
import json
import random
import threading
import time

import os.path
current_dir = os.path.dirname(os.path.abspath(__file__))

je = json.JSONEncoder()

def non_blocking_quickstart(root=None, script_name="", config=None):
    """Mount the given root, start the builtin server (and engine), then block.
    
    root: an instance of a "controller class" (a collection of page handler
        methods) which represents the root of the application.
    script_name: a string containing the "mount point" of the application.
        This should start with a slash, and be the path portion of the URL
        at which to mount the given root. For example, if root.index() will
        handle requests to "http://www.example.com:8080/dept/app1/", then
        the script_name argument would be "/dept/app1".
        
        It MUST NOT end in a slash. If the script_name refers to the root
        of the URI, it MUST be an empty string (not "/").
    config: a file or dict containing application config. If this contains
        a [global] section, those entries will be used in the global
        (site-wide) config.
    """
    if config:
        cherrypy._global_conf_alias.update(config)
    
    cherrypy.tree.mount(root, script_name, config)
    
    if hasattr(cherrypy.engine, "signal_handler"):
        cherrypy.engine.signal_handler.subscribe()
    if hasattr(cherrypy.engine, "console_control_handler"):
        cherrypy.engine.console_control_handler.subscribe()
    
    cherrypy.engine.start()
    #engine.block()


CONSOLE_HTML = ("""
<html>
  <head>
  <style>
    p {font-family: monospace;color: #fff;}
    body {background-color: #000;}
  </style>

    <script type="text/javascript" src="/static/jquery-1.9.0.min.js"></script>
    <script type="text/javascript" src="/static/piui.js"></script>
    <script type="text/javascript">

$(document).ready(function() {
  consolePoll();
});
    </script> 
  </head>
  <body>
    <p id="console"></p>
  </body>
</html>
""")

INDEX_HTML = """
<html>
  <head>

    <script type="text/javascript" src="/static/jquery-1.9.0.min.js"></script>
    <script type="text/javascript">

$(document).ready(function() {
  window.location.href = '%s';
});
    </script> 
  </head>
  <body>
  </body>
</html>
"""

UI_HTML = ("""
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <title>%s</title>
    <meta name="viewport" content="initial-scale=1, maximum-scale=1, user-scalable=no">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black">

    <link rel="stylesheet" href="/static/ratchet.css">
    <script src="/static/ratchet.js"></script>
    <script type="text/javascript" src="/static/jquery-1.9.0.min.js"></script>
    <script type="text/javascript" src="/static/piui.js"></script>
    <script type="text/javascript">

$(document).ready(function() {
  poll();
});
    </script> 
  </head>
  <body>
  <header class="bar-title">
    <h1 class="title">%s</h1>
  </header>

  <div class="content">
  <div class="content-padded">

  <p id="end"></p>
  </div>
  </div>

  </body>
</html>
""")


class Handlers(object):

    MAX_MESSAGES_TO_BUFFER = 40

    def __init__(self, lock):
        self._lock = lock
        self._msgs = []
        self._current_page = '/'
        self._current_page_title = ''
        self._current_page_obj = None
        self._in_buffer = []

    def index(self):
        print self._current_page
        return INDEX_HTML % (self._current_page)
    index.exposed = True

    def ui(self):
        return UI_HTML % (self._current_page_title, self._current_page_title)
    ui.exposed = True

    def console(self):
        return CONSOLE_HTML
    console.exposed = True

    def click(self, eid):
        if self._current_page_obj:
            self._current_page_obj.handle_click(eid)
    click.exposed = True

    def toggle(self, eid, v):
        if self._current_page_obj:
            self._current_page_obj.handle_toggle(eid, v)
    toggle.exposed = True

    def new_page(self, page_name, title='', page_obj=None):
        self._current_page = '/' + page_name
        self._current_page_title = title
        self._current_page_obj = page_obj
        self.flush_queue()
        self.enqueue({"cmd": "newpage", "page": page_name})

    def enqueue(self, msg):
        self._lock.acquire()
        self._msgs.insert(0, msg)
        if len(self._msgs) > self.MAX_MESSAGES_TO_BUFFER:
            self._msgs.pop()
        self._lock.release()

    def enqueue_and_result(self, msg):
        self._lock.acquire()
        self._msgs.insert(0, msg)
        if len(self._msgs) > self.MAX_MESSAGES_TO_BUFFER:
            self._msgs.pop()
        done = False
        self._lock.release()
        while not done:
            time.sleep(0.1)
            self._lock.acquire()
            done = len(self._msgs) == 0
            self._lock.release()
        ready = False
        result = None
        while not ready:
            time.sleep(0.1)
            self._lock.acquire()
            ready = len(self._in_buffer) > 0
            if ready:
                result = self._in_buffer.pop()
            self._lock.release()
        return result


    def flush_queue(self):
        self._lock.acquire()
        self._msgs = []
        self._lock.release()

    def poll(self):
        waited = 0
        msg = None
        while waited < 500:
            self._lock.acquire()
            if not self._msgs == []:
                msg = self._msgs.pop()
            self._lock.release()
            if msg:
                return je.encode(msg)
            time.sleep(0.01)
            waited = waited + 1
        return je.encode({'cmd': 'timeout'})
    poll.exposed = True

    def state(self, msg):
        self._lock.acquire()
        self._in_buffer.append(msg)
        self._lock.release()
    state.exposed = True


class PiUiConsole(object):

    def __init__(self, piui):
        self._piui = piui

    def print_line(self, line):
        self._piui._handlers.enqueue({"cmd": "print", "msg": line})


class PiUiTextbox(object):

    def __init__(self, text, element, piui):
        self._piui = piui
        self._id = 'textbox_' + str(int(random.uniform(0, 1e16)))
        self._piui._handlers.enqueue(
            {'cmd': 'addelement', 'e': element, 'eid': self._id, 'txt': text})

    def set_text(self, text):
        self._piui._handlers.enqueue(
          {'cmd': 'updateinner', 'eid': self._id, 'txt': text})

class PiUiInput(object):

    def __init__(self, input_type, piui, placeholder):
        self._piui = piui
        self._id = 'input_' + str(int(random.uniform(0, 1e16)))
        self._piui._handlers.enqueue(
            {'cmd': 'addinput', 'eid': self._id, 'type': input_type,
             'placeholder': placeholder})

    def get_text(self):
        text = self._piui._handlers.enqueue_and_result({'cmd': 'getinput', 'eid': self._id})
        return text

class PiUiListItem(object):

    def __init__(self, piui, parent_id, item_text, chevron, toggle, onclick, ontoggle):
        self._piui = piui
        self._parent_id = parent_id
        self._on_click = onclick
        self._on_toggle = ontoggle
        self._id = 'li_' + str(int(random.uniform(0, 1e16)))
        self._toggle_id = 'tg_' + str(int(random.uniform(0, 1e16)))
        ch_flag = '0'
        tg_flag = '0'
        if chevron:
          ch_flag = '1'
        if toggle:
          tg_flag = '1'
        self._piui._handlers.enqueue({'cmd': 'addli', 'eid': self._id, 'pid': self._parent_id,
            'txt': item_text, 'chevron': ch_flag, 'toggle': tg_flag, 'tid': self._toggle_id})

class PiUiList(object):
    """A PiUi page element representing an HTML <ul>."""
    def __init__(self, piui, page):
        self._piui = piui
        self._page = page
        self._id = 'ul_' + str(int(random.uniform(0, 1e16)))
        self._piui._handlers.enqueue({'cmd': 'addul', 'eid': self._id})

    def add_item(self, item_text, chevron=False, toggle=False, onclick=None, ontoggle=None):
        item = PiUiListItem(self._piui, self._id, item_text,
                            chevron, toggle, onclick, ontoggle)
        self._page._clickables[item._id] = item
        self._page._toggleables[item._toggle_id] = item
        return item

class PiUiButton(object):

    def __init__(self, text, piui, on_click):
        self._piui = piui
        self._id = 'button_' + str(int(random.uniform(0, 1e16)))
        self._piui._handlers.enqueue({'cmd': 'addbutton', 'eid': self._id, 'txt': text})
        self._on_click = on_click

    def set_text(self, text):
        self._piui._handlers.enqueue({'cmd': 'updateinner', 'eid': self._id, 'txt': text})


class PiUiImage(object):

    def __init__(self, src, piui):
        self._piui = piui
        self._id = 'image_' + str(int(random.uniform(0, 1e16)))
        self._piui._handlers.enqueue(
            {'cmd': 'addimage', 'eid': self._id, 'src': src})

    def set_src(self, src):
        self._piui._handlers.enqueue({'cmd': 'setimagesrc', 'eid': self._id, 'src': src})

class PiUiPage(object):

    def __init__(self, piui, title):
        self._piui = piui
        self._title = title
        self._elements = []
        self._clickables = {}
        self._toggleables = {}
        self._inputs = {}

    def add_textbox(self, text, element="p"):
        txtbox = PiUiTextbox(text, element, self._piui)
        self._elements.append(txtbox)
        return txtbox

    def add_element(self, element):
        ele = PiUiTextbox("", element, self._piui)
        self._elements.append(ele)
        return ele

    def add_button(self, text, on_click):
        button = PiUiButton(text, self._piui, on_click)
        self._elements.append(button)
        self._clickables[button._id] = button
        return button

    def add_input(self, input_type, placeholder=""):
        edit = PiUiInput(input_type, self._piui, placeholder)
        self._elements.append(edit)
        self._inputs[edit._id] = edit
        return edit

    def add_image(self, src):
        img = PiUiImage(src, self._piui)
        self._elements.append(img)
        return img

    def add_list(self):
        new_list = PiUiList(self._piui, self)
        self._elements.append(new_list)
        return new_list

    def handle_click(self, eid):
        button = self._clickables[eid]
        if button and button._on_click:
            button._on_click()

    def handle_toggle(self, eid, value):
        toggle = self._toggleables[eid]
        val = False
        if (value == 'true'):
          val = True
        if toggle and toggle._on_toggle:
            toggle._on_toggle(val)


class AndroidPiUi(object):

    def __init__(self, img_dir=''):
        self._lock = threading.Lock()
        self._handlers = Handlers(self._lock)
        cherrypy.config.update({'server.socket_host': '0.0.0.0',
                                'server.socket_port': 9999})
        conf = {'/static': 
                  {'tools.staticdir.on': True,
                   'tools.staticdir.dir': os.path.join(current_dir, 'static')},
                '/imgs':
                  {'tools.staticdir.on': True,
                   'tools.staticdir.dir': img_dir}}
        non_blocking_quickstart(self._handlers, config=conf)

    def console(self):
        self._handlers.new_page('console')
        return PiUiConsole(self)

    def new_ui_page(self, title=''):
        page = PiUiPage(self, title)
        self._handlers.new_page('ui', title=title, page_obj=page)
        return page

    def done(self):
        cherrypy.engine.block()
