import json
import unittest
import urllib2

from piui import PiUi

class NetworkInfoTestCase(unittest.TestCase):

    def setUp(self):
        self._ui = PiUi("Test")

    def tearDown(self):
        print "tearDown"
        self._ui.exit()

    def http_get(self, rel_url):
        handler = urllib2.urlopen('http://localhost:9999/' + rel_url)
        return handler.getcode(), handler.read()


    def test_console(self):
        con = self._ui.console()
        resp = self.http_get('/')
        assert "window.location.href = '/console';" in resp[1]
        resp = self.http_get('/console')
        assert "consolePoll();" in resp[1]
        resp = self.http_get('/poll')


if __name__ == '__main__':
    unittest.main()