from gdo.base.Cache import gdo_cached, Cache
from gdo.base.GDO import GDO
from gdo.base.GDT import GDT
from gdo.core.GDO_User import GDO_User
from gdo.core.GDT_AutoInc import GDT_AutoInc
from gdo.core.GDT_Bool import GDT_Bool
from gdo.core.GDT_User import GDT_User
from gdo.date.GDT_Created import GDT_Created
from gdo.date.GDT_Timestamp import GDT_Timestamp
from gdo.message.GDT_Message import GDT_Message
from gdo.pm.GDT_PMFolder import GDT_PMFolder
from gdo.ui.GDT_Title import GDT_Title


class GDO_PM(GDO):

    def gdo_columns(self) -> list[GDT]:
        return [
            GDT_AutoInc('pm_id'),
            GDT_PMFolder('pm_folder').not_null().cascade_delete(),
            GDT_User('pm_from').not_null(),
            GDT_User('pm_to').not_null().cascade_delete(),
            GDT_User('pm_owner').not_null().cascade_delete(),
            GDT_Title('pm_title').not_null(),
            GDT_Message('pm_message').not_null(),
            GDT_Bool('pm_encrypted').not_null(),
            GDT_Timestamp('pm_read'),
            GDT_Created('pm_created'),
        ]

    def gdo_cached(self) -> bool:
        return False

    def get_owner(self) -> GDO_User:
        return self.gdo_value('pm_owner')

    def render_title(self) -> str:
        return self.gdo_val('pm_title')

    @classmethod
    def unread_count(cls, user: GDO_User) -> int:
        if (cached := Cache.get('new_pm_count', user.get_id())) is not None:
            return cached
        count = cls.table().count_where(f'pm_owner={user.get_id()} AND pm_read IS NULL')
        return Cache.set('new_pm_count', user.get_id(), count)

