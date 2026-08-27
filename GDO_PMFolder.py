from gdo.base.GDO import GDO
from gdo.base.GDT import GDT
from gdo.core.GDT_AutoInc import GDT_AutoInc
from gdo.core.GDT_Creator import GDT_Creator
from gdo.core.GDT_Name import GDT_Name


class GDO_PMFolder(GDO):

    def gdo_cached(self) -> bool:
        # Folder rows are augmented with the current user's live PM count.
        return False

    def gdo_columns(self) -> list[GDT]:
        return [
            GDT_AutoInc('pmf_id'),
            GDT_Name('pmf_name').label('name'),
            GDT_Creator('pmf_owner').not_null(False),
        ]
