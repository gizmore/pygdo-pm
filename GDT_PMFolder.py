from gdo.core.GDT_ObjectSelect import GDT_ObjectSelect
from gdo.pm.GDO_PMFolder import GDO_PMFolder


class GDT_PMFolder(GDT_ObjectSelect):

    def __init__(self, name):
        super().__init__(name)
        self.table(GDO_PMFolder.table())
