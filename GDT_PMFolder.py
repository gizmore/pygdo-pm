from gdo.core.GDO_User import GDO_User
from gdo.core.GDT_ObjectSelect import GDT_ObjectSelect
from gdo.pm.GDO_PMFolder import GDO_PMFolder


class GDT_PMFolder(GDT_ObjectSelect):

    def __init__(self, name):
        super().__init__(name)
        self.table(GDO_PMFolder.table())

    async def gdo_choices(self) -> dict:
        uid = GDO_User.current().get_id()
        return GDO_PMFolder.table().select().where(f'pmf_owner IS NULL OR pmf_owner = {uid}').exec().fetch_all_dict()
