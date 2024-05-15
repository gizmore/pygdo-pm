from gdo.base.GDO import GDO
from gdo.pm.GDO_PMFolder import GDO_PMFolder
from gdo.table.MethodQueryTable import MethodQueryTable


class folders(MethodQueryTable):

    def gdo_table(self) -> GDO:
        return GDO_PMFolder.table()


