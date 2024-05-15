from gdo.base.GDO import GDO
from gdo.pm.GDO_PM import GDO_PM
from gdo.table.MethodQueryTable import MethodQueryTable


class folder(MethodQueryTable):

    def gdo_table(self) -> GDO:
        return GDO_PM.table()
