import os
import unittest

from gdo.base.Application import Application
from gdo.base.ModuleLoader import ModuleLoader
from gdo.core.GDO_User import GDO_User
from gdo.core.connector.Web import Web
from gdo.pm.GDO_PM import GDO_PM
from gdo.pm.module_pm import module_pm
from gdotest.TestUtil import reinstall_module, cli_plug, GDOTestCase, web_plug, WebPlug, cli_gizmore, web_gizmore, install_module


class PMTest(GDOTestCase):
    peter: GDO_User
    other: GDO_User

    async def asyncSetUp(self):
        await super().asyncSetUp()
        Application.init(os.path.dirname(__file__ + "/../../../../"))
        loader = ModuleLoader.instance()
        loader.load_modules_db(True)
        loader.init_modules(True, True)
        install_module('pm')
        loader.init_cli()
        self.peter = await Web.get_server().get_or_create_user('Peter')
        self.peter._authenticated = True
        self.other = await Web.get_server().get_or_create_user('SearchOther')
        self.other._authenticated = True
        cli_gizmore()
        web_gizmore()

    def test_00_install(self):
        reinstall_module('pm')
        self.assertIsInstance(module_pm.instance(), module_pm, "Installation failed")

    def test_01_test_send_usage(self):
        result = cli_plug(self.peter, '$pm.send')
        self.assertIn('message', result, 'Message field is not mentioned in pm.send error.')
        self.assertNotIn('[message]', result, 'Message field should not be optional in pm.send error.')
        self.assertIn('message\x1b', result, 'Message field does not show error in pm.send error.')

    def test_02_forgot_msg(self):
        result = cli_plug(self.peter, '$pm.send giz "Hi There"')
        self.assertIn('message\x1b', result, 'Message field does not show error in pm.send error.')
        self.assertIn('Too many results', result, 'Message field does not show ambiguous error in pm.send error.')

    def test_03_send_pm_from_peter_to_gizmore(self):
        target = web_gizmore()
        result = cli_plug(self.peter, f'$pm.send {target.get_id()} "Hi There" <b>Message<i>Body</i></b>')
        self.assertIn('has been sent', result, 'Message sending does not work.')
        self.assertEqual('1', GDO_PM.unread_count(cli_gizmore()))
        result = cli_plug(cli_gizmore(), "$pm.next")
        self.assertIn('Hi There', result, "PM Reading does not work")
        self.assertIn('\x1b[1mMessage\x1b[3mBody\x1b[0m\x1b[0m', result, "PM Reading does not work #2")
        self.assertEqual('0', GDO_PM.unread_count(cli_gizmore()))

    def test_03b_send_pm_from_web_form(self):
        target = web_gizmore()
        out = web_plug('pm.send.html?_lang=en').user('Peter').post({
            'to': target.get_id(),
            'title': 'Web PM',
            'message_input': 'Web message body',
            'submit': 'Submit',
        }).exec()
        self.assertIn('has been sent', out)
        pm = GDO_PM.table().get_by_vals({
            'pm_owner': target.get_id(),
            'pm_title': 'Web PM',
        })
        self.assertIsNotNone(pm)
        self.assertEqual('Web message body', pm.gdo_val('pm_message_input'))

    def test_04_folders(self):
        out = web_plug("pm.folders.html?_lang=en&of=pmf_name%20ASC").user("gizmore").exec()
        self.assertIn("order_pmf_count", out, "Web overview does not render nicely.")
        self.assertIn("pm.overview.folder.1.html", out, "PM folder names do not link to the overview folder view.")

    def test_05_searches_object_sender_name_in_folder(self):
        target = web_gizmore()
        hit = cli_plug(self.peter, f'$pm.send {target.get_id()} "Sender Search Hit" Match')
        miss = cli_plug(self.other, f'$pm.send {target.get_id()} "Sender Search Miss" Ignore')
        self.assertIn('has been sent', hit)
        self.assertIn('has been sent', miss)

        out = web_plug('pm.list.html?_lang=en&folder=1&s=Peter').user('gizmore').exec()
        self.assertIn('Sender Search Hit', out)
        self.assertNotIn('Sender Search Miss', out)

        sent = cli_plug(target, f'$pm.send {self.peter.get_id()} "Recipient Search Hit" Match')
        self.assertIn('has been sent', sent)
        out = web_plug('pm.list.html?_lang=en&folder=2&s=Peter').user('gizmore').exec()
        self.assertIn('Recipient Search Hit', out)

    async def test_06_pm_overview_web(self):
        target = web_gizmore()
        out = cli_plug(self.peter, f'$pm.send {target.get_id()} "Hi There" Message Body')
        self.assertIn('has been sent', out, 'Message sending does not work.')

    def test_07_pm_overview(self):
        WebPlug.COOKIES = {}
        out = web_plug("pm.overview.html").exec()
        self.assertIn('execute this method', out, "PM Center is not restricted to authenticated users.")

    def test_08_pm_overview_ok(self):
        out = web_plug("pm.overview.html?_lang=en&_o=pm_title%20DESC").user("gizmore").exec()
        self.assertIn("Compose PM", out, "PM overview does not link to the compose form.")
        self.assertIn("order_pmf_count", out, "Web overview does not render nicely.")

    def test_09_pm_settings(self):
        out = web_plug('account.settings.html?_lang=en&module=pm').user('gizmore').post({'email_on_pm': '1', 'submit_pm': '1'}).exec()
        set = web_gizmore().get_setting_val('email_on_pm')
        self.assertEqual('1', set, 'Cannot set PM setting')

    def test_10_profile_message_links(self):
        from gdo.mail.module_mail import module_mail

        target = web_gizmore()
        module_mail.instance().set_email_for(target, 'gizmore@example.test')
        out = web_plug(f'user.profile.for.{target.get_id()}.html?_lang=en').user('Peter').exec()
        self.assertIn(f'pm.send.to.{target.get_id()}.html', out)
        self.assertIn(f'mail.send.to.{target.get_id()}.html', out)

        pm_form = web_plug(f'pm.send.to.{target.get_id()}.html?_lang=en').user('Peter').exec()
        self.assertIn('Send PM', pm_form)
        mail_form = web_plug(f'mail.send.to.{target.get_id()}.html?_lang=en').user('Peter').exec()
        self.assertIn('Send Email', mail_form)


if __name__ == '__main__':
    unittest.main()
