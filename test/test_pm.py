import os
import unittest
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock, patch

from gdo.base.Application import Application
from gdo.base.ModuleLoader import ModuleLoader
from gdo.core.GDO_User import GDO_User
from gdo.core.connector.Web import Web
from gdo.base.util.href import href
from gdo.pm.GDO_PM import GDO_PM
from gdo.pm.method.folder import folder
from gdo.pm.method.folders import folders
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
        self.assertEqual('0', GDO_PM.unread_count(cli_gizmore()))

    def test_sending_pm_emits_new_pm_ipc_outside_tests(self):
        from gdo.pm.method.send import send

        with (
            patch.object(Application, 'IS_TEST', False),
            patch('gdo.pm.method.send.IPC.send') as ipc,
        ):
            send().send_pm(self.peter, self.other, 'IPC test', 'Private message')
        ipc.assert_called_once_with('pm.ipc_new_pm', (self.other.get_id(),))

    async def test_new_pm_ipc_runs_the_login_delivery(self):
        from gdo.pm.method.ipc_new_pm import ipc_new_pm

        module = module_pm.instance()
        method = ipc_new_pm().env_user(GDO_User.system()).env_server(self.other.get_server())
        method.input('recipient_user_id', str(self.other.get_id()))
        with (
            patch.object(Application, 'IS_DOG', True),
            patch.object(Application, 'IS_TEST', False),
            patch.object(module, 'on_user_login', new=AsyncMock()) as on_user_login,
        ):
            await method.execute()
        on_user_login.assert_awaited_once_with(self.other)

    def test_pm_participants_render_as_profile_links(self):
        pm = GDO_PM.blank({
            'pm_from': self.peter.get_id(),
            'pm_to': web_gizmore().get_id(),
        })
        rendered = pm.column('pm_from').render_cell()
        self.assertIn(
            href('user', 'profile', f'&for={self.peter.get_id()}-{self.peter.get_name_sid()}'),
            rendered)
        self.assertIn('title="Level: ', rendered)
        self.assertIn(' | Score: ', rendered)
        self.assertLess(rendered.index('<a '), rendered.index('<img '))
        self.assertLess(rendered.index('<img '), rendered.index('</a>'))

    def test_folder_created_renders_datetime_and_age(self):
        pm = GDO_PM.blank({'pm_created': '2026-09-26 15:30:00.000'})
        rendered = folder().render_pm_created(pm.column('pm_created'), pm)
        self.assertRegex(rendered, r'^\d{2}/\d{2}/\d{4} \d{2}:\d{2} \(.+\)$')
        self.assertNotRegex(rendered, r'^\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}')

    def test_unread_pm_title_has_a_new_icon(self):
        unread = GDO_PM.blank({'pm_title': 'Unread', 'pm_read': None})
        rendered = folder().render_pm_title(unread.column('pm_title'), unread)
        self.assertIn('fa-star', rendered)
        self.assertIn('color: var(--gdo-new)', rendered)

        read = GDO_PM.blank({'pm_title': 'Read', 'pm_read': '2026-09-27 08:30:00.000'})
        self.assertNotIn('fa-star', folder().render_pm_title(read.column('pm_title'), read))

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

    def test_03c_send_pm_to_self_uses_inbox_and_sentbox(self):
        user = web_gizmore()
        title = f'Self PM {uuid4().hex}'
        result = cli_plug(user, f'$pm.send {user.get_id()} "{title}" Body')
        self.assertIn('has been sent', result)
        rows = GDO_PM.table().all(
            f"pm_owner={user.get_id()} AND pm_title='{title}'"
        )
        self.assertEqual(2, len(rows))
        self.assertEqual({'1', '2'}, {pm.gdo_val('pm_folder') for pm in rows})

    def test_04_folders(self):
        out = web_plug("pm.folders.html?_lang=en&of=pmf_name%20ASC").user("gizmore").exec()
        self.assertIn("pm.overview.folder.1.html", out, "PM folder names do not link to the overview folder view.")
        self.assertIn('class="shrink table table-striped table-bordered"', out)

    def test_folder_renders_shrink_participant_cells(self):
        out = web_plug("pm.list.html?_lang=en&folder=1").user("gizmore").exec()
        self.assertIn('class="shrink"', out)

    def test_folder_orders_newest_private_messages_first(self):
        self.assertEqual('pm_created DESC', folder().gdo_order_default())

    def test_pm_read_without_id_selects_the_oldest_unread_message(self):
        from gdo.pm.method.view import view

        method = view().env_user(self.peter)
        query = MagicMock()
        with patch.object(GDO_PM, 'table') as table:
            table.return_value.select.return_value.where.return_value.first.return_value.order.return_value = query
            method.get_unread_pm()
        table.return_value.select.return_value.where.assert_called_once_with(
            f'pm_owner={self.peter.get_id()} AND pm_read IS NULL'
        )
        query.exec.assert_called_once()

    def test_pm_folder_reset_uses_its_form_href(self):
        method = folder()
        method.get_form().href('/pm.overview.html?folder=1&f=unread&s=hello&o=pm_title+ASC&page=2&keep=yes')
        self.assertEqual(
            '/pm.overview.html?folder=1&keep=yes',
            method.table_reset_href(),
        )

    def test_folders_do_not_render_table_headers(self):
        self.assertFalse(folders().gdo_render_table_headers())

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
        self.assertIn('aria-label="create Icon"', out, "PM overview compose link has no create icon.")
        self.assertNotIn("order_pmf_count", out, "PM folder table should not render headers.")

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

    async def test_welcome_pm_respects_the_module_setting(self):
        module = module_pm.instance()
        module.cfg_welcome_pm = MagicMock(return_value=False)
        with patch('gdo.pm.method.send.send.send_pm') as send_pm:
            await module.on_user_created(self.peter)
        send_pm.assert_not_called()

        module.cfg_welcome_pm.return_value = True
        module.cfg_welcome_sender = MagicMock(return_value=web_gizmore())
        with (
            patch('gdo.pm.method.send.send.send_pm') as send_pm,
            patch('gdo.pm.module_pm.t', side_effect=('Welcome', 'Hello %s')),
            patch('gdo.pm.module_pm.sitename', return_value='PyGDO'),
        ):
            await module.on_user_created(self.peter)
        send_pm.assert_called_once()

    async def test_user_login_delivers_every_unread_pm(self):
        module = module_pm.instance()
        user = MagicMock()
        owner = MagicMock()
        owner.get_id.return_value = 23
        user.get_effective_user.return_value = owner
        first = MagicMock()
        second = MagicMock()
        query = MagicMock()
        query.exec.return_value.fetch_all.return_value = [first, second]

        with (
            patch.object(Application, 'IS_TEST', False),
            patch.object(GDO_PM, 'table') as table,
            patch.object(module, 'deliver_pm', new=AsyncMock()) as deliver,
        ):
            table.return_value.select.return_value.where.return_value.order.return_value = query
            await module.on_user_login(user)

        self.assertEqual(
            'pm_owner=23 AND pm_read IS NULL',
            table.return_value.select.return_value.where.call_args.args[0],
        )
        self.assertEqual([((user, owner, first), {}), ((user, owner, second), {})], [
            (call.args, call.kwargs) for call in deliver.await_args_list
        ])

    async def test_user_login_delivery_uses_pm_view(self):
        module = module_pm.instance()
        user = MagicMock()
        owner = MagicMock()
        pm = MagicMock()
        pm.get_id.return_value = 42
        server = MagicMock()
        connector = MagicMock()
        connector.get_render_mode.return_value = Application.get_mode()
        connector.send_to_user = AsyncMock()
        user.get_server.return_value = server
        server.get_connector.return_value = connector
        card = MagicMock()
        card.render.return_value = 'Private message body'
        method = MagicMock()
        method.env_http.return_value = method
        method.env_user.return_value = method
        method.env_server.return_value = method
        method.input.return_value = method
        method.execute = AsyncMock(return_value=card)

        with patch('gdo.pm.method.view.view', return_value=method) as view_method:
            await module.deliver_pm(user, owner, pm)

        view_method.assert_called_once_with()
        method.input.assert_called_once_with('id', '42')
        connector.send_to_user.assert_awaited_once()
        message = connector.send_to_user.await_args.args[0]
        self.assertIs(user, message._env_user)
        self.assertEqual('Private message body', message._result)


if __name__ == '__main__':
    unittest.main()
