from gdo.base.GDT import GDT
from gdo.core.GDO_User import GDO_User
from gdo.core.GDT_RestOfText import GDT_RestOfText
from gdo.core.GDT_User import GDT_User
from gdo.form.GDT_Form import GDT_Form
from gdo.form.MethodForm import MethodForm
from gdo.pm.GDO_PM import GDO_PM
from gdo.ui.GDT_Title import GDT_Title


class send(MethodForm):

    def gdo_create_form(self, form: GDT_Form) -> None:
        form.add_field(
            GDT_User('target').not_null(),
            GDT_Title('title').not_null(),
            GDT_RestOfText('message').not_null(),
        )
        super().gdo_create_form(form)

    def form_submitted(self) -> GDT:
        sender = self._env_user
        target = self.param_value('target') # type: GDO_User
        title = self.param_value('title')
        message = self.param_value('message')
        self.create_pm(sender, target, title, message, sender)
        self.create_pm(sender, target, title, message, target)
        return self.reply('msg_pm_sent', [target.render_name()])

    def create_pm(self, sender: GDO_User, target: GDO_User, title: str, message: str, owner: GDO_User):
        pm = GDO_PM.blank({
            'pm_from': sender.get_id(),
            'pm_to': target.get_id(),
            'pm_owner': owner.get_id(),
            'pm_title': self.get_title(title, owner),
            'pm_message': self.get_message(title, owner),
            'pm_encrypted': self.get_encrypted(owner),
        }).insert()


