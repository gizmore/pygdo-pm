from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.core.GDT_Container import GDT_Container
from gdo.pm.method.compose import compose
from gdo.pm.method.folder import folder
from gdo.pm.method.folders import folders


class overview(Method):

    def gdo_user_type(self) -> str | None:
        return 'member,guest,link'

    async def gdo_execute(self) -> GDT:
        cont = GDT_Container().add_field(
            compose().env_copy(self).args_copy(self),
            folders().env_copy(self).args_copy(self),
            folder().env_copy(self).args_copy(self)
        )
        return cont
