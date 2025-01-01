from gdo.base.GDT import GDT
from gdo.core.GDO_User import GDO_User
from gdo.core.GDT_User import GDT_User
from gdo.form.GDT_Form import GDT_Form
from gdo.form.MethodForm import MethodForm
from gdo.mail.method.send import send
from gdo.message.GDT_Message import GDT_Message
from gdo.ui.GDT_Title import GDT_Title


class to(MethodForm):

    def gdo_trigger(self) -> str:
        return ''

    def gdo_parameters(self) -> list[GDT]:
        return [
            GDT_User('target').not_null(),
        ]

    def gdo_create_form(self, form: GDT_Form) -> None:
        form.add_field(
            GDT_Title('title').not_null(),
            GDT_Message('message').not_null(),
        )
        form.href()
        super().gdo_create_form(form)

    def form_submitted(self):
        self.send_pm(self._env_user, self.param_value('user'), self.param_val('title'), self.param_val('message'))
        return self.redirect(self.gdo_module().href('overview'))

    def send_pm(self, sender: GDO_User, recipient: GDO_User, title: str, message: str):
        send().env_copy(self).args_copy(self).form_submitted()
