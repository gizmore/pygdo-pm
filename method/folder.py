from gdo.base.GDO import GDO
from gdo.base.GDT import GDT
from gdo.base.Query import Query
from gdo.base.Util import href
from gdo.core.GDT_User import GDT_User
from gdo.pm.GDO_PM import GDO_PM
from gdo.pm.GDT_PMFolder import GDT_PMFolder
from gdo.table.MethodQueryTable import MethodQueryTable
from gdo.ui.GDT_Link import GDT_Link
from gdo.ui.GDT_Title import GDT_Title


class folder(MethodQueryTable):

    def gdo_paginate_size(self) -> int:
        return 1

    def gdo_table(self) -> GDO:
        return GDO_PM.table()

    def gdo_parameters(self) -> list[GDT]:
        return [
            GDT_PMFolder('folder').initial('1').not_null(),
        ]

    def gdo_table_headers(self) -> list[GDT]:
        return self.gdo_table().columns_only('pm_from', 'pm_to', 'pm_title', 'pm_created')

    def gdo_table_query(self) -> Query:
        user = self._env_user
        fid = self.param_val('folder')
        return super().gdo_table_query().where(f'pm_owner={user.get_id()} AND pm_folder={fid}')

    def render_pm_title(self, gdt: GDT_Title, gdo: GDO) -> str:
        return GDT_Link().text_raw(gdt.get_val()).href(href('pm', 'view', f'&id={gdo.get_id()}')).render()
