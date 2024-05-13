from gdo.base.GDT import GDT
from gdo.core.GDT_RestOfText import GDT_RestOfText
from gdo.core.GDT_User import GDT_User
from gdo.form.GDT_Form import GDT_Form
from gdo.form.MethodForm import MethodForm
from gdo.ui.GDT_Title import GDT_Title


class send(MethodForm):

    def gdo_create_form(self, form: GDT_Form) -> None:
        form.add_field(
            GDT_User('to').not_null(),
            GDT_Title('title').not_null(),
            GDT_RestOfText('text').not_null(),
        )
        super().gdo_create_form(form)

    def form_submitted(self) -> GDT:
        to = self.param_value('to')
        return self.reply('msg_pm_sent')


