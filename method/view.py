from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.core.GDT_Object import GDT_Object
from gdo.date.Time import Time
from gdo.form.GDT_Form import GDT_Form
from gdo.form.GDT_Validator import GDT_Validator
from gdo.pm.GDO_PM import GDO_PM
from gdo.ui.GDT_Card import GDT_Card


class view(Method):

    def gdo_trigger(self) -> str:
        return 'pm.read'

    def gdo_parameters(self) -> [GDT]:
        return [
            GDT_Object('id').table(GDO_PM.table()).not_null(),
            GDT_Validator().validator(None, 'id', self.validate_pm_owner),
        ]

    def validate_pm_owner(self, form: GDT_Form, field: GDT, value: GDO_PM) -> bool:
        if value is None:
            return True
        if value.get_owner() != self._env_user:
            return self.err('err_permission', ['owner'])
        return True

    def get_pm(self) -> GDO_PM:
        return self.param_value('id')

    def gdo_execute(self) -> GDT:
        pm = self.get_pm()
        if pm.gdo_val('pm_read') is None:
            pm.save_val('pm_read', Time.get_date())
        card = GDT_Card()
        card.add_field(*pm.columns_only('pm_from', 'pm_to', 'pm_title', 'pm_message'))
        return card
