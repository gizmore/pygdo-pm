from gdo.base.GDO import GDO
from gdo.base.GDT import GDT
from gdo.core.GDT_AutoInc import GDT_AutoInc
from gdo.core.GDT_Bool import GDT_Bool
from gdo.core.GDT_User import GDT_User
from gdo.date.GDT_Created import GDT_Created
from gdo.pm.GDT_PMFolder import GDT_PMFolder
from gdo.ui.GDT_Message import GDT_Message
from gdo.ui.GDT_Title import GDT_Title


class GDO_PM(GDO):

    def gdo_columns(self) -> list[GDT]:
        return [
            GDT_AutoInc('pm_id'),
            GDT_PMFolder('pm_folder').not_null(),
            GDT_User('pm_from').not_null(),
            GDT_User('pm_to').not_null(),
            GDT_User('pm_owner').not_null(),
            GDT_Title('pm_title').not_null(),
            GDT_Message('pm_message').not_null(),
            GDT_Bool('pm_encrypted').not_null(),
            GDT_Created('pm_created'),
        ]
