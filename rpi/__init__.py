import cherrypy
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


CONSOLE_HTML = """
<html>
  <head>
  <style>
    p {font-family: monospace;color: #fff;}
    body {background-color: #000;}
</style>

    <script type="text/javascript" src="/static/jquery-1.9.0.min.js"></script>
    <script type="text/javascript">

function poll() {
  $.get("/poll", {}, function(xml) {
       setTimeout(function() {poll()}, 0);
       if (xml != "--timeout--") {
           // format and output result
           $('<p>' + xml + '</p>').insertBefore('#console');
           $('html, body').animate({scrollTop: $(document).height()}, 'slow');
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
"""

class Handlers(object):

    def __init__(self, lock):
        self._lock = lock
        self._msgs = []

    def index(self):
        return self.msg
    index.exposed = True

    def console(self):
        return CONSOLE_HTML
    console.exposed = True

    def new_page(self, page_name):
        pass

    def enqueue(self, msg):
        self._lock.acquire()
        self._msgs.insert(0, msg)
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


class PiUiConsole(object):

    def __init__(self, piui):
        self._piui = piui

    def print_line(self, line):
        self._piui.print_line(line)

class AndroidPiUi(object):

    def __init__(self):
        self._lock = threading.Lock()
        self._handlers = Handlers(self._lock)
        cherrypy.config.update({'server.socket_port': 9999})
        conf = {'/static': {'tools.staticdir.on': True, 'tools.staticdir.dir': os.path.join(current_dir, 'static')}}
        non_blocking_quickstart(self._handlers, config=conf)

    def console(self):
        self._handlers.new_page('/console')
        return PiUiConsole(self)

    def print_line(self, line):
        self._handlers.enqueue(line)

    def done(self):
        cherrypy.engine.block()
