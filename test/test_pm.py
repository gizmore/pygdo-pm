import os
import unittest

from gdo.base.Application import Application
from gdo.base.ModuleLoader import ModuleLoader
from gdo.core.GDO_User import GDO_User
from gdo.core.connector.Web import Web
from gdotest.TestUtil import reinstall_module, cli_plug


class PMTest(unittest.TestCase):
    peter: GDO_User

    def setUp(self):
        Application.init(os.path.dirname(__file__ + "/../../../../"))
        loader = ModuleLoader.instance()
        loader.load_modules_db(True)
        loader.init_modules()
        reinstall_module('pm')
        loader.init_cli()
        self.peter = Web.get_server().get_or_create_user('Peter')
        return self

    def test_01_test_send_usage(self):
        result = cli_plug(self.peter, 'pm.send')
        self.assertIn('to', result, 'To field is not mentioned in pm.send error.')

    def test_02_send_pm(self):
        result = cli_plug(self.peter, 'pm.send giz "Hi There" "This is a pm"')
        self.assertIn('Too many', result, "GDT_User does not work.")

if __name__ == '__main__':
    unittest.main()
