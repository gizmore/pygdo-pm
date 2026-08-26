from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.core.GDT_Container import GDT_Container
from gdo.pm.method.folder import folder
from gdo.pm.method.folders import folders
from gdo.ui.GDT_Link import GDT_Link


class overview(Method):

    @classmethod
    def gdo_trigger(cls) -> str:
        return ''

    def gdo_user_type(self) -> str | None:
        return 'member,guest,link'

    def gdo_execute(self) -> GDT:
        cont = GDT_Container().add_fields(
            GDT_Link().href(self.gdo_module().href('send')).text('link_pm_compose'),
            folders().env_copy(self).args_copy(self),
            folder().env_copy(self).args_copy(self)
        )
        return cont
