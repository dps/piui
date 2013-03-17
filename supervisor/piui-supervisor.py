#!/usr/bin/python

import cherrypy
import subprocess

import os.path
current_dir = os.path.dirname(os.path.abspath(__file__))


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