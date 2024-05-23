from gdo.base.GDO import GDO
from gdo.base.GDT import GDT
from gdo.base.Query import Query
from gdo.core.GDT_UInt import GDT_UInt
from gdo.pm.GDO_PMFolder import GDO_PMFolder
from gdo.table.MethodQueryTable import MethodQueryTable


class folders(MethodQueryTable):

    def gdo_table(self) -> GDO:
        return GDO_PMFolder.table()

    def gdo_searched(self) -> bool:
        return False

    def gdo_paginated(self) -> bool:
        return False

    def gdo_filtered(self) -> bool:
        return False

    def gdo_order_name(self) -> str:
        return 'of'

    def gdo_table_headers(self) -> list[GDT]:
        t = self.gdo_table()
        return [
            t.column('pmf_name'),
            GDT_UInt('pmf_count').label('count'),
        ]

    def gdo_table_query(self) -> Query:
        uid = self._env_user.get_id()
        query = super().gdo_table_query()
        query.select(f'(SELECT COUNT(*) FROM gdo_pm WHERE pm_folder = gdo_pmfolder.pmf_id AND pm_owner={uid}) AS pmf_count')
        query.where(f'pmf_owner IS NULL OR pmf_owner={uid}')
        return query
