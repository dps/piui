import cherrypy
import random
import threading
import time

import os.path
current_dir = os.path.dirname(os.path.abspath(__file__))

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


DISPATCH_JS = """
function dispatch(msg) {
    if (msg === "--timeout--") {
      // Do nothing, will re-poll
      return null;
    } else if (msg.indexOf("--newpage--") == 0) {
      newpage = msg.substring("--newpage--".length, msg.length);
      window.location.href = newpage;
      return null;
    } else {
      return msg;
    }
}
"""

CONSOLE_HTML = ("""
<html>
  <head>
  <style>
    p {font-family: monospace;color: #fff;}
    body {background-color: #000;}
</style>

    <script type="text/javascript" src="/static/jquery-1.9.0.min.js"></script>
    <script type="text/javascript">
""" + DISPATCH_JS +
"""
function poll() {
  $.get("/poll", {}, function(xml) {
       setTimeout(function() {poll()}, 0);
       xml = dispatch(xml);
       if (xml != null) {
           // format and output result
           $('<p>' + xml + '</p>').insertBefore('#console');
           $('html, body').animate({scrollTop: $(document).height()}, 'fast');
       }
     });    
}

$(document).ready(function() {
  poll();
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

    <!-- Sets initial viewport load and disables zooming  -->
    <meta name="viewport" content="initial-scale=1, maximum-scale=1, user-scalable=no">

    <!-- Makes your prototype chrome-less once bookmarked to your phone's home screen -->
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black">

    <!-- Include the compiled Ratchet CSS -->
    <link rel="stylesheet" href="/static/ratchet.css">

    <!-- Include the compiled Ratchet JS -->
    <script src="/static/ratchet.js"></script>
    <script type="text/javascript" src="/static/jquery-1.9.0.min.js"></script>
    <script type="text/javascript">
""" + DISPATCH_JS +
"""

var BEFORE = "#end";

function poll() {
  $.get("/poll", {}, function(xml) {
       setTimeout(function() {poll()}, 0);
       xml = dispatch(xml);
       if (xml != null) {
         if (xml.indexOf('--addelement') == 0) {
           var parts = xml.split('-');
           e = parts[3];
           eid = parts[4];
           txt = parts[5];
           $('<' + e + ' id="' + eid + '">' + txt + '</' + e + '>').insertBefore(BEFORE);
         } else if (xml.indexOf('--updateinner') == 0) {
           var parts = xml.split('-');
           eid = parts[3];
           txt = parts[4];
           $('#' + eid).html(txt);
         } else if (xml.indexOf('--addbutton') == 0) {
           var parts = xml.split('-');
           eid = parts[3];
           txt = parts[4];
           $('<a class="button" id="' + eid + '">' + txt + '</a>').insertBefore(BEFORE);
           $('#' + eid).click(function(o) {
              $.get('/click?eid=' + $(this).attr('id'), {}, function (r) {});
            });
         } else if (xml.indexOf('--startspan') == 0) {
           $('<span id="sp"><div id="espn"></span>').insertBefore('#end');
           BEFORE = "#espn";
         } else if (xml.indexOf('--endspan') == 0) {
           BEFORE = "#end";
         } else if (xml.indexOf('--addinput') == 0) {
           var parts = xml.split('-');
           eid = parts[3];
           type = parts[4];
           placeholder = parts[5];
           $('<input id="' + eid + '" type="' + type +'" placeholder = "' + placeholder +'">').insertBefore(BEFORE);
         } else if (xml.indexOf('--getinput') == 0) {
           var parts = xml.split('-');
           eid = parts[3];
           $.get('/state?msg=' + $('#' + eid).val(), {}, function (r) {});
         } else if (xml.indexOf('--addimage') == 0) {
           var parts = xml.split('-');
           eid = parts[3];
           src = parts[4];
           $('<img id="' + eid + '" src="/imgs/' + src +'">').insertBefore(BEFORE);
         } else if (xml.indexOf('--setimagesrc') == 0) {
           var parts = xml.split('-');
           eid = parts[3];
           src = parts[4];
           $('#' + eid).attr('src', '/imgs/' + src);
         } 
       }
     });    
}

$(document).ready(function() {
  poll();
});
    </script> 
  </head>
  <body>

  <!-- Make sure all your bars are the first things in your <body> -->
  <header class="bar-title">
    <h1 class="title">%s</h1>
  </header>

  <!-- Wrap all non-bar HTML in the .content div (this is actually what scrolls) -->
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

    def new_page(self, page_name, title='', page_obj=None):
        self._current_page = '/' + page_name
        self._current_page_title = title
        self._current_page_obj = page_obj
        self.flush_queue()
        self.enqueue('--newpage--%s' % page_name)

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
                return msg
            time.sleep(0.01)
            waited = waited + 1
        return "--timeout--"
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
        self._piui.print_line(line)


class PiUiTextbox(object):

    def __init__(self, text, element, piui):
        self._piui = piui
        self._id = 'textbox_' + str(int(random.uniform(0, 1e16)))
        self._piui._handlers.enqueue('--addelement-%s-%s-%s' % (
            element, self._id, text))

    def set_text(self, text):
        self._piui._handlers.enqueue('--updateinner-%s-%s' % (self._id, text))

class PiUiInput(object):

    def __init__(self, input_type, piui, placeholder):
        self._piui = piui
        self._id = 'input_' + str(int(random.uniform(0, 1e16)))
        self._piui._handlers.enqueue('--addinput-%s-%s-%s' % (self._id, input_type, placeholder))

    def get_text(self):
        text = self._piui._handlers.enqueue_and_result('--getinput-%s' % (self._id))
        return text

class PiUiButton(object):

    def __init__(self, text, piui, on_click):
        self._piui = piui
        self._id = 'button_' + str(int(random.uniform(0, 1e16)))
        self._piui._handlers.enqueue('--addbutton-%s-%s' % (self._id, text))
        self._on_click = on_click

    def set_text(self, text):
        self._piui._handlers.enqueue('--updateinner-%s-%s' % (self._id, text))

class PiUiImage(object):

    def __init__(self, src, piui):
        self._piui = piui
        self._id = 'image_' + str(int(random.uniform(0, 1e16)))
        self._piui._handlers.enqueue('--addimage-%s-%s' % (self._id, src))

    def set_src(self, src):
        self._piui._handlers.enqueue('--setimagesrc-%s-%s' % (self._id, src))


class PiUiPage(object):

    def __init__(self, piui, title):
        self._piui = piui
        self._title = title
        self._elements = []
        self._buttons = {}
        self._inputs = {}

    def add_textbox(self, text, element="p"):
        txtbox = PiUiTextbox(text, element, self._piui)
        self._elements.append(txtbox)
        return txtbox

    def add_button(self, text, on_click):
        button = PiUiButton(text, self._piui, on_click)
        self._elements.append(button)
        self._buttons[button._id] = button
        return button

    def add_input(self, input_type, placeholder=""):
        edit = PiUiInput(input_type, self._piui, placeholder)
        self._elements.append(edit)
        self._inputs[edit._id] = edit
        return edit

    def start_span(self):
        self._piui._handlers.enqueue('--startspan')

    def end_span(self):
        self._piui._handlers.enqueue('--endspan')

    def add_image(self, src):
        img = PiUiImage(src, self._piui)
        self._elements.append(img)
        return img

    def handle_click(self, eid):
        button = self._buttons[eid]
        if button:
            button._on_click()


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

    def print_line(self, line):
        self._handlers.enqueue(line)

    def done(self):
        cherrypy.engine.block()
