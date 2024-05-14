import os
import unittest

from gdo.base.Application import Application
from gdo.base.ModuleLoader import ModuleLoader
from gdo.core.GDO_User import GDO_User
from gdo.core.connector.Web import Web
from gdotest.TestUtil import reinstall_module, cli_plug, GDOTestCase


class PMTest(GDOTestCase):
    peter: GDO_User

    def setUp(self):
        Application.init(os.path.dirname(__file__ + "/../../../../"))
        loader = ModuleLoader.instance()
        loader.load_modules_db(True)
        loader.init_modules()
        reinstall_module('pm')
        loader.init_cli()
        self.peter = Web.get_server().get_or_create_user('Peter')
        super().setUp()

    def test_01_test_send_usage(self):
        result = cli_plug(self.peter, 'pm.send')
        self.assertIn('target', result, 'Target field is not mentioned in pm.send error.')
        self.assertIn('message', result, 'Message field is not mentioned in pm.send error.')
        self.assertNotIn('[message]', result, 'Message field should not be optional in pm.send error.')
        self.assertIn('message\x1b', result, 'Message field does not show error in pm.send error.')

    def test_02_forgot_msg(self):
        result = cli_plug(self.peter, 'pm.send giz "Hi There"')
        self.assertIn('message\x1b', result, 'Message field does not show error in pm.send error.')
        self.assertIn('Too many results', result, 'Message field does not show ambigious error in pm.send error.')

    def test_03_send_pm_from_peter_to_gizmore(self):
        result = cli_plug(self.peter, 'pm.send gizmore{1} "Hi There" Message Body')
        self.assertIn('has been sent', result, 'Message sending does not work.')



if __name__ == '__main__':
    unittest.main()
