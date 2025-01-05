from gdo.core.GDT_User import GDT_User
from gdo.form.GDT_Form import GDT_Form
from gdo.form.MethodForm import MethodForm


class compose(MethodForm):

    def gdo_trigger(self) -> str:
        return ''

    def gdo_create_form(self, form: GDT_Form) -> None:
        form.add_field(GDT_User('to').not_null())
        super().gdo_create_form(form)

    def form_submitted(self):
        return self.redirect(self.gdo_module().href('send', f"&to={self.param_value('to').get_id()}"))
