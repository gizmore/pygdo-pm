from gdo.base.GDO_Module import GDO_Module
from gdo.base.GDT import GDT
from gdo.core.GDO_User import GDO_User
from gdo.core.GDT_Bool import GDT_Bool
from gdo.pm.GDO_PM import GDO_PM
from gdo.pm.GDO_PMFolder import GDO_PMFolder
from gdo.ui.GDT_Link import GDT_Link
from gdo.ui.GDT_Page import GDT_Page


class module_pm(GDO_Module):

    def gdo_friendencies(self):
        return [
            'gpg',
            'mail',
        ]

    def gdo_classes(self):
        return [
            GDO_PM,
            GDO_PMFolder,
        ]

    def gdo_install(self):
        GDO_PMFolder.blank({
            'pmf_id': '1',
            'pmf_name': 'InBox',
        }).soft_replace()
        GDO_PMFolder.blank({
            'pmf_id': '2',
            'pmf_name': 'SentBox',
        }).soft_replace()

    def gdo_module_config(self) -> list[GDT]:
        return [
            GDT_Bool('mail_on_pm').initial('1'),
        ]

    def cfg_email_on_pm(self) -> bool:
        return self.get_config_value('mail_on_pm')

    def gdo_user_settings(self) -> list[GDT]:
        settings = []
        if self.cfg_email_on_pm():
            settings.append(GDT_Bool('email_on_pm').initial('0'))
        return settings

    def gdo_init_sidebar(self, page: 'GDT_Page'):
        user = GDO_User.current()
        if user.is_authenticated():
            page._right_bar.add_field(GDT_Link().href(self.href('overview')).text('link_pm', [1]))


