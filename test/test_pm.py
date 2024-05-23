import os
import unittest

from gdo.base.Application import Application
from gdo.base.ModuleLoader import ModuleLoader
from gdo.core.GDO_User import GDO_User
from gdo.core.connector.Web import Web
from gdotest.TestUtil import reinstall_module, cli_plug, GDOTestCase, web_plug, WebPlug, cli_gizmore, install_module, web_gizmore


class PMTest(GDOTestCase):
    peter: GDO_User

    def setUp(self):
        Application.init(os.path.dirname(__file__ + "/../../../../"))
        loader = ModuleLoader.instance()
        loader.load_modules_db(True)
        loader.init_modules()
        install_module('pm')
        loader.init_cli()
        self.peter = Web.get_server().get_or_create_user('Peter')
        cli_gizmore()
        web_gizmore()
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
        result = cli_plug(self.peter, 'pm.send gizmore{2} "Hi There" Message Body')
        self.assertIn('has been sent', result, 'Message sending does not work.')

    def test_04_folders(self):
        out = web_plug("pm.folders.html?_lang=en&of=pm_title%20DESC&of=pm_title%20ASC").user("gizmore").exec()
        self.assertIn("order_pmf_count", out, "Web overview does not render nicely.")

    def test_04_pm_overview_web(self):
        out = cli_plug(self.peter, 'pm.send gizmore{2} "Hi There" Message Body')
        self.assertIn('has been sent', out, 'Message sending does not work.')

        WebPlug.COOKIES = {}
        out = web_plug("pm.overview.html").exec()
        self.assertIn('authenticate', out, "PM Center is not restricted to authenticated users.")

        out = web_plug("pm.overview.html?_lang=en&_o=pm_title%20DESC").user("gizmore").exec()
        self.assertIn("order_pmf_count", out, "Web overview does not render nicely.")




if __name__ == '__main__':
    unittest.main()
