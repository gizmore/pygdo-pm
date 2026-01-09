from gdo.avatar.GDT_Avatar import GDT_Avatar
from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.core.GDT_Object import GDT_Object
from gdo.core.GDT_String import GDT_String
from gdo.date.Time import Time
from gdo.form.GDT_Form import GDT_Form
from gdo.form.GDT_Validator import GDT_Validator
from gdo.pm.GDO_PM import GDO_PM
from gdo.ui.GDT_Card import GDT_Card
from gdo.user.GDT_ProfileLink import GDT_ProfileLink


class view(Method):

    @classmethod
    def gdo_trigger(cls) -> str:
        return 'pm.read'

    def gdo_parameters(self) -> list[GDT]:
        return [
            GDT_Object('id').table(GDO_PM.table()).not_null(),
            GDT_Validator().validator(None, 'id', self.validate_pm_owner),
        ]

    def validate_pm_owner(self, form: GDT_Form, field: GDT, value: GDO_PM) -> bool:
        if value is None:
            return True
        if value.get_owner() != self._env_user:
            return self.err('err_permission', ('owner',))
        return True

    def get_pm(self) -> GDO_PM:
        return self.param_value('id')

    def gdo_execute(self) -> GDT:
        pm = self.get_pm()
        if pm.gdo_val('pm_read') is None:
            pm.save_val('pm_read', Time.get_date())
        card = GDT_Card().gdo(pm)
        card.title_raw(pm.render_title())
        card.image(GDT_Avatar('avatar').for_user(self._env_user))
        # card.get_header().add_field(GDT_ProfileLink().user(pm.get_other_user(self._env_user)))
        card.get_header().add_fields(pm.column('pm_from'), GDT_String('btw').text('%s', ('->', )))
        card.get_header().add_fields(*pm.columns_only('pm_to', 'pm_title'))
        card.get_content().add_fields(pm.column('pm_message'))
        card.get_footer().add_field(pm.column('pm_created'))
        return card
