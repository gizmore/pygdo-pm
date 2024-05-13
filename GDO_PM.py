from gdo.base.GDO import GDO
from gdo.base.GDT import GDT
from gdo.core.GDT_AutoInc import GDT_AutoInc


class GDO_PM(GDO):

    def gdo_columns(self) -> list[GDT]:
        return [
            GDT_AutoInc('pm_id'),

        ]
