import json
import unittest
import urllib

from piui import PiUi

class PiUiTestCase(unittest.TestCase):

    def setUp(self):
        self._ui = PiUi("Test", timeout=1)

    def tearDown(self):
        print("tearDown")
        self._ui.exit()

    def http_get(self, rel_url):
        handler = urllib.request.urlopen('http://localhost:9999' + rel_url)
        return handler.getcode(), handler.read().decode()

    def click(self):
        self._clicked = True

    def test_menu(self):
        self.page = self._ui.new_ui_page(title="PiUi")
        self.list = self.page.add_list()
        self.list.add_item("Static Content", chevron=True, onclick=self.click)
        self.list.add_item("Buttons", chevron=True, onclick=self.click)
        self.list.add_item("Input", chevron=True, onclick=self.click)
        self.list.add_item("Images", chevron=True, onclick=self.click)
        self.list.add_item("Toggles", chevron=True, onclick=self.click)
        self.list.add_item("Console!", chevron=True, onclick=self.click)
        resp = self.http_get('/')
        assert "initPiUi();" in resp[1]
        resp = self.http_get('/init')
        assert "ok" in resp[1]
        resp = self.http_get('/poll')
        assert '"cmd": "newpage"' in resp[1]
        resp = self.http_get('/poll')
        assert '"cmd": "pagepost"' in resp[1]
        resp = self.http_get('/poll')
        assert '"cmd": "addul"' in resp[1]
        resp = self.http_get('/poll')
        assert '"cmd": "addli"' in resp[1]
        resp = self.http_get('/poll')
        assert '"cmd": "addli"' in resp[1]
        resp = self.http_get('/poll')
        assert '"cmd": "addli"' in resp[1]
        resp = self.http_get('/poll')
        assert '"cmd": "addli"' in resp[1]
        resp = self.http_get('/poll')
        assert '"cmd": "addli"' in resp[1]
        resp = self.http_get('/poll')
        assert '"cmd": "addli"' in resp[1]
        resp = self.http_get('/poll')
        assert '"cmd": "timeout"' in resp[1]

    def test_clicks(self):
        self._clicked = False
        self.page = self._ui.new_ui_page(title="PiUi")
        self.title = self.page.add_textbox("Buttons!", "h1")
        plus = self.page.add_button("Test Button", self.click)
        resp = self.http_get('/')
        assert "initPiUi();" in resp[1]
        resp = self.http_get('/init')
        assert "ok" in resp[1]
        resp = self.http_get('/poll')
        assert '"cmd": "newpage"' in resp[1]
        resp = self.http_get('/poll')
        assert '"cmd": "pagepost"' in resp[1]
        resp = self.http_get('/poll')
        assert '"cmd": "addelement"' in resp[1]
        resp = self.http_get('/poll')
        assert '"cmd": "addbutton"' in resp[1]
        btn_cmd = resp[1]
        resp = self.http_get('/poll')
        assert '"cmd": "timeout"' in resp[1]
        decoder = json.JSONDecoder()
        cmd = decoder.decode(btn_cmd)
        self.http_get('/click?eid=' + cmd['eid'])
        assert self._clicked


if __name__ == '__main__':
    unittest.main()