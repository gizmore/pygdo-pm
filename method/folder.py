from typing import Any

from gdo.base.GDO import GDO
from gdo.base.GDT import GDT
from gdo.base.Query import Query
from gdo.base.Render import Mode
from gdo.base.util.href import href
from gdo.date.GDT_Timestamp import GDT_Timestamp
from gdo.date.Time import Time
from gdo.pm.GDO_PM import GDO_PM
from gdo.pm.GDT_PMFolder import GDT_PMFolder
from gdo.table.MethodQueryTable import MethodQueryTable
from gdo.ui.GDT_Link import GDT_Link
from gdo.ui.GDT_Title import GDT_Title


class folder(MethodQueryTable):

    @classmethod
    def gdo_trigger(cls) -> str:
        return 'pm.list'

    def gdo_table(self) -> GDO:
        return GDO_PM.table()

    def gdo_parameters(self) -> list[GDT]:
        return [
            GDT_PMFolder('folder').initial('1').not_null(),
        ]

    def gdo_render_pagination_top(self) -> bool:
        return False

    def gdo_table_headers(self) -> list[GDT]:
        return self.gdo_table().columns_only('pm_from', 'pm_to', 'pm_title', 'pm_created')

    def gdo_order_default(self):
        return 'pm_created DESC'

    def gdo_table_query(self) -> Query:
        user = self._env_user
        fid = self.param_val('folder')
        return super().gdo_table_query().where(f'pm_owner={user.get_id()} AND pm_folder={fid}')

    def render_pm_title(self, gdt: GDT_Title, gdo: GDO) -> str:
        icon = 'star' if gdo.is_unread() else None
        return GDT_Link().text_raw(gdt.get_val()).href(
            href('pm', 'view', f'&id={gdo.get_id()}')
        ).icon(icon, color='var(--gdo-new)').render()

    def render_pm_created(self, gdt: GDT_Timestamp, gdo: GDO) -> str:
        """Show the exact send time and its relative age in PM folders."""
        return f'{gdt.render_format(Time.FMT_SHORT)} ({gdt.render_format(Time.FMT_AGO)})'

    def render_gdo(self, gdo: GDO, mode: Mode) -> Any:
        return f'{gdo.get_id()}-{gdo.gdo_val('pm_title')}'
