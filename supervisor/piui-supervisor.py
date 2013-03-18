#!/usr/bin/python

import cherrypy
import json
import subprocess

import os.path
current_dir = os.path.dirname(os.path.abspath(__file__))

APP_CONFIG_FILE = "supervisor.conf"
running_app = None

def parse_config():
    apps = []
    try:
      conf_file = file(current_dir + '/' + APP_CONFIG_FILE, 'r')
      for line in conf_file.readlines():
        name, loc = line.split(' ')
        apps.append((name, loc))
    except IOError:
        pass
    return apps

class ProcHandlers(object):

    def _proc_read(self, filename):
        return '\n'.join(file('/proc/' + filename, 'r').readlines())

    def version(self):
        return self._proc_read('version')
    version.exposed = True

    def meminfo(self):
        return self._proc_read('meminfo')
    meminfo.exposed = True

class SupHandlers(object):

    proc = ProcHandlers()

    def uptime(self):
        return subprocess.check_output('uptime')
    uptime.exposed = True

    def lsusb(self):
        return subprocess.check_output('lsusb')
    lsusb.exposed = True

    def ps(self):
        return subprocess.check_output(['ps', '-ef'])
    ps.exposed = True

    def ifconfig(self):
        return subprocess.check_output('ifconfig')
    ifconfig.exposed = True

    def w(self):
        return subprocess.check_output('w')
    w.exposed = True

    def listapps(self):
        apps = parse_config()
        app_names = [a[0] for a in apps]
        return json.JSONEncoder().encode(app_names)
    listapps.exposed = True

    def startapp(self, appname):
        global running_app
        if (running_app):
            running_app.kill()
        apps = {}
        for (name, loc) in parse_config():
            apps[name] = loc
        if apps.has_key(appname):
            loc = apps[name]
            cmd_line = 'python ' + loc
            running_app = subprocess.Popen(cmd_line, shell=True)
            return 'ok ' + cmd_line
        return 'not found'
    startapp.exposed = True

    def killapp(self):
        global running_app
        if (running_app):
            running_app.kill()
            return 'killed'
        else:
            return 'not found'
    killapp.exposed = True

    def ping(self):
        return 'pong'
    ping.exposed = True


class Handlers(object):
    sup = SupHandlers()


class PiUiSupervisor(object):

    def __init__(self):
        self._handlers = Handlers()
        cherrypy.config.update({'server.socket_host': '0.0.0.0',
                                'server.socket_port': 9000})
        cherrypy.quickstart(self._handlers)



if __name__ == "__main__":
    sup = PiUiSupervisor()