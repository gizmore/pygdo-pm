from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.pm.GDO_PM import GDO_PM
from gdo.pm.method.view import view


class view_next(Method):

    @classmethod
    def gdo_trigger(cls) -> str:
        return 'pm.next'

    def gdo_execute(self) -> GDT:
        user = self._env_user
        if pm := (GDO_PM.table().select().where(f'pm_owner={user.get_id()} and pm_read IS NULL').order('pm_created ASC')
                .first().exec().fetch_object()):
            return view().env_copy(self).input('id', pm.get_id()).execute()
        else:
            return self.msg('msg_no_more_new_pm')
