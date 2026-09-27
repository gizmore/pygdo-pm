from gdo.base.Application import Application
from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.core.GDT_User import GDT_User
from gdo.pm.module_pm import module_pm


class ipc_new_pm(Method):
    """Ask the Dog to deliver unread PMs for one recipient after a new PM."""

    @classmethod
    def gdo_trigger(cls) -> str:
        return ''

    def gdo_parameters(self) -> list[GDT]:
        return [GDT_User('recipient_user_id').not_null().positional()]

    async def gdo_execute(self) -> GDT:
        if Application.IS_DOG:
            await module_pm.instance().on_user_login(
                self.param_value('recipient_user_id')
            )
        return self.empty()
