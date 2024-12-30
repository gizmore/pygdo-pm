from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.core.GDT_Object import GDT_Object
from gdo.date.Time import Time
from gdo.pm.GDO_PM import GDO_PM
from gdo.ui.GDT_Card import GDT_Card


class view(Method):

    def gdo_trigger(self) -> str:
        return 'pm.read'

    def gdo_parameters(self) -> [GDT]:
        return [
            GDT_Object('id').table(GDO_PM.table()),
        ]

    def get_pm(self) -> GDO_PM:
        return self.param_value('id')

    def gdo_execute(self) -> GDT:
        pm = self.get_pm()
        if pm.gdo_val('pm ')is_unread():
        pm.save_val('pm_read', Time.get_date())
        card = GDT_Card()
        card.add_field(*pm.table().columns_only('pm_from', 'pm_to,', 'pm_title', 'pm_message'))
        return card
