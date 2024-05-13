from gdo.base.GDO_Module import GDO_Module
from gdo.core.GDO_User import GDO_User
from gdo.pm.GDO_PM import GDO_PM
from gdo.ui.GDT_Link import GDT_Link
from gdo.ui.GDT_Page import GDT_Page


class module_pm(GDO_Module):

    def gdo_classes(self):
        return [
            GDO_PM,
        ]

    def gdo_init_sidebar(self, page: 'GDT_Page'):
        user = GDO_User.current()
        if user.is_authenticated():
            page._right_bar.add_field(GDT_Link().href(self.href('overview')).text('link_pm', [1]))


